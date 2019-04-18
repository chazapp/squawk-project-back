package models

import java.util.UUID

import play.api.libs.json.Json

case class Sources(
  link: String,
  host: String)
{}

object Sources {
  implicit val sourcesJsonFormat = Json.format[Sources]
}
