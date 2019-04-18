package models

import java.util.UUID

import play.api.libs.json.Json

import com.mohiva.play.silhouette.api.{Identity, LoginInfo}
import com.mohiva.play.silhouette.api.util.PasswordInfo

case class Profile(
  loginInfo:LoginInfo,
  confirmed: Boolean,
  email: Option[String],
  username: Option[String],
  sources: Option[List[Sources]],
  passwordInfo: Option[PasswordInfo]) {
}

case class User(id: UUID, profiles: List[Profile]) extends Identity {
  def profileFor(loginInfo:LoginInfo) = profiles.find(_.loginInfo == loginInfo)
}

object User {
  implicit val passwordInfoJsonFormat = Json.format[PasswordInfo]
  implicit val profileJsonFormat = Json.format[Profile]
  implicit val userJsonFormat = Json.format[User]
}
