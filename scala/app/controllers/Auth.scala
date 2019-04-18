package controllers

import java.util.UUID
import javax.inject.Inject

import scala.concurrent.Future
import scala.concurrent.duration._

import net.ceedubs.ficus.Ficus._

import com.mohiva.play.silhouette.api.Authenticator.Implicits._
import com.mohiva.play.silhouette.api.{Environment,LoginInfo,Silhouette}
import com.mohiva.play.silhouette.api.exceptions.ProviderException
import com.mohiva.play.silhouette.api.repositories.AuthInfoRepository
import com.mohiva.play.silhouette.api.services.AvatarService
import com.mohiva.play.silhouette.api.util.{Credentials,PasswordHasher}
import com.mohiva.play.silhouette.impl.authenticators.CookieAuthenticator
import com.mohiva.play.silhouette.impl.exceptions.IdentityNotFoundException
import com.mohiva.play.silhouette.impl.providers._

import play.api._
import play.api.data.Form
import play.api.data.Forms._
import play.api.data.validation.Constraints._
import play.api.mvc._
import play.api.i18n.{I18nSupport,MessagesApi,Messages}
import play.api.libs.concurrent.Execution.Implicits._

import models.{Profile,User,UserToken, Sources}
import services.{UserService,UserTokenService}

import org.joda.time.DateTime

object AuthForms {

  // Sign up
  case class SignUpData(email:String, password:String, username:String)
  def signUpForm(implicit messages:Messages) = Form(mapping(
      "email" -> email,
      "password" -> tuple(
        "password1" -> nonEmptyText.verifying(minLength(6)),
        "password2" -> nonEmptyText
      ).verifying(Messages("error.passwordsDontMatch"), password => password._1 == password._2),
      "username" -> nonEmptyText
    )
    ((email, password, username) => SignUpData(email, password._1, username))
    (signUpData => Some((signUpData.email, ("",""), signUpData.username)))
  )

  // Sign in
  case class SignInData(email:String, password:String, rememberMe:Boolean)
  val signInForm = Form(mapping(
      "email" -> email,
      "password" -> nonEmptyText,
      "rememberMe" -> boolean
    )(SignInData.apply)(SignInData.unapply)
  )

}

class Auth @Inject() (
  val messagesApi: MessagesApi,
  val env:Environment[User,CookieAuthenticator],
  authInfoRepository: AuthInfoRepository,
  credentialsProvider: CredentialsProvider,
  userService: UserService,
  userTokenService: UserTokenService,
  avatarService: AvatarService,
  passwordHasher: PasswordHasher,
  configuration: Configuration) extends Silhouette[User,CookieAuthenticator] {

  import AuthForms._

  def startSignUp = UserAwareAction.async { implicit request =>
    Future.successful(request.identity match {
      case Some(user) => Redirect(routes.Application.index)
      case None => Ok(views.html.auth.startSignUp(signUpForm))
    })
  }

  def handleStartSignUp = Action.async { implicit request =>
    signUpForm.bindFromRequest.fold(
      bogusForm => Future.successful(BadRequest(views.html.auth.startSignUp(bogusForm))),
      signUpData => {
        val loginInfo = LoginInfo(CredentialsProvider.ID, signUpData.email)
        userService.retrieve(loginInfo).flatMap {
          case Some(_) =>
            Future.successful(Redirect(routes.Auth.startSignUp()).flashing(
              "error" -> Messages("error.userExists", signUpData.email)))
          case None =>
            val profile = Profile(
              loginInfo = loginInfo,
              confirmed = false,
              email = Some(signUpData.email),
              username = Some(signUpData.username),
              sources = None,
              passwordInfo = None)
            for {
              user <- userService.save(User(id = UUID.randomUUID(), profiles = List(profile)))
              _ <- authInfoRepository.add(loginInfo, passwordHasher.hash(signUpData.password))
              token <- userTokenService.save(UserToken.create(user.id, signUpData.email, true))
            } yield {
              Redirect(routes.Auth.signUp(token.id.toString).absoluteURL())
              // Ok(views.html.auth.finishSignUp(profile))
            }
        }
      }
    )
  }

  def signUp(tokenId:String) = Action.async { implicit request =>
    val id = UUID.fromString(tokenId)
    userTokenService.find(id).flatMap {
      case None =>
        Future.successful(NotFound(views.html.errors.notFound(request)))
      case Some(token) if token.isSignUp && !token.isExpired =>
        userService.find(token.userId).flatMap {
          case None => Future.failed(new IdentityNotFoundException(Messages("error.noUser")))
          case Some(user) =>
            val loginInfo = LoginInfo(CredentialsProvider.ID, token.email)
            for {
              authenticator <- env.authenticatorService.create(loginInfo)
              value <- env.authenticatorService.init(authenticator)
              _ <- userService.confirm(loginInfo)
              _ <- userTokenService.remove(id)
              result <- env.authenticatorService.embed(value, Redirect(routes.Application.index()))
            } yield result
        }
      case Some(token) =>
        userTokenService.remove(id).map {_ => NotFound(views.html.errors.notFound(request))}
    }
  }

  def signIn = UserAwareAction.async { implicit request =>
    Future.successful(request.identity match {
      case Some(user) => Redirect(routes.Application.index())
      case None => Ok(views.html.auth.signIn(signInForm))
    })
  }

  def authenticate = Action.async { implicit request =>
    signInForm.bindFromRequest.fold(
      bogusForm => Future.successful(BadRequest(views.html.auth.signIn(bogusForm))),
      signInData => {
        val credentials = Credentials(signInData.email, signInData.password)
        credentialsProvider.authenticate(credentials).flatMap { loginInfo =>
          userService.retrieve(loginInfo).flatMap {
            case None =>
              Future.successful(Redirect(routes.Auth.signIn()).flashing("error" -> Messages("error.noUser")))
            case Some(user) if !user.profileFor(loginInfo).map(_.confirmed).getOrElse(false) =>
              Future.successful(Redirect(routes.Auth.signIn()).flashing("error" -> Messages("error.unregistered", signInData.email)))
            case Some(_) => for {
              authenticator <- env.authenticatorService.create(loginInfo).map {
                case authenticator if signInData.rememberMe =>
                  val c = configuration.underlying
                  authenticator.copy(
                    expirationDateTime = new DateTime() + c.as[FiniteDuration]("silhouette.authenticator.rememberMe.authenticatorExpiry"),
                    idleTimeout = c.getAs[FiniteDuration]("silhouette.authenticator.rememberMe.authenticatorIdleTimeout"),
                    cookieMaxAge = c.getAs[FiniteDuration]("silhouette.authenticator.rememberMe.cookieMaxAge")
                  )
                case authenticator => authenticator
              }
              value <- env.authenticatorService.init(authenticator)
              result <- env.authenticatorService.embed(value, Redirect(routes.Application.index()))
            } yield result
          }
        }.recover {
          case e:ProviderException => Redirect(routes.Auth.signIn()).flashing("error" -> Messages("error.invalidCredentials"))
        }
      }
    )
  }

  def signOut = SecuredAction.async { implicit request =>
    env.authenticatorService.discard(request.authenticator, Redirect(routes.Application.index()))
  }

}
