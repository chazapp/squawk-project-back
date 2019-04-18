package daos

import com.mohiva.play.silhouette.api.LoginInfo
import com.mohiva.play.silhouette.api.util.PasswordInfo

import java.util.UUID

import scala.concurrent.Await
import scala.concurrent.duration.DurationInt

import play.api.libs.concurrent.Execution.Implicits.defaultContext
import play.api.test._
import play.api.test.Helpers._

import models.{User, Profile}

trait DaoSpecResources {

  val timeout = DurationInt(10).seconds
  def fakeApp = FakeApplication(additionalConfiguration = Map("mongodb.uri" -> "mongodb://localhost:27017/test"))

  def setupUser(userDao:MongoUserDao, user:User) {
    Await.ready(userDao.users.drop(), timeout)
    Await.result(userDao.save(user).map(_ => ()), timeout)
  }

  def withUserDao[T](t:MongoUserDao => T):T = running(fakeApp) {
    val userDao = new MongoUserDao
    Await.ready(userDao.users.drop(), timeout)
    t(userDao)
  }

  def withPasswordInfoDao[T](t:PasswordInfoDao => T):T = running(fakeApp) {
    val userDao = new MongoUserDao
    val passwordInfoDao = new PasswordInfoDao
    setupUser(userDao, cleanTestUser)
    t(passwordInfoDao)
  }

  val loginInfo = LoginInfo(providerID="credentials", providerKey="john.doe@gmail.com")
  val passwordInfo = PasswordInfo(hasher="BCrypt", password="kittens", salt=None)

  val testPasswordProfile = Profile(
    loginInfo = loginInfo,
    confirmed=false,
    email = Some("john.doe@email.com"),
    firstName = Some("John"),
    lastName = Some("Doe"),
    fullName = Some("John Doe"),
    passwordInfo = None,
    avatarUrl = Some("http://www.gravatar.com"))

    val cleanTestUser = User(UUID.randomUUID(), List(testPasswordProfile))
    val credentialsTestUser = User(UUID.randomUUID(), List(testPasswordProfile.copy(passwordInfo = Some(passwordInfo))))
}
