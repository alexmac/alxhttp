import asyncio
from datetime import datetime
import logging
from typing import Annotated, Dict, List, Optional

from asyncpg import create_pool
from asyncpg.pool import Pool
from aiohttp.typedefs import Middleware
from alxhttp.pydantic.basemodel import BaseModel, Empty
from alxhttp.pydantic.request import Request
from alxhttp.pydantic.response import Response
from alxhttp.pydantic.route import add_route, route
from alxhttp.schemas import prefixed_id
from alxhttp.server import Server
from alxhttp.sql import SQLValidator


class ExampleServer(Server):
  def __init__(self, pool: Pool, middlewares: Optional[List[Middleware]] = None, logger: Optional[logging.Logger] = None):
    super().__init__(middlewares=middlewares, logger=logger)
    self.pool = pool


class GoogleAccount(BaseModel):
  sub: str
  email: str | None
  email_verified: bool | None
  hd: str | None
  name: Optional[str]
  picture: Optional[str]
  given_name: Optional[str]
  family_name: Optional[str]
  created_at: datetime
  updated_at: datetime


UserID = Annotated[str, prefixed_id('u_')]


class User(BaseModel):
  user_id: UserID
  created_at: datetime
  updated_at: datetime
  google: Optional[GoogleAccount]


OrgID = Annotated[str, prefixed_id('org_')]


class MatchInfo(BaseModel):
  org_id: OrgID


class UsersWithRoles(User):
  roles: List[str]


class OrgUsers(BaseModel):
  org_id: OrgID
  users: Dict[UserID, UsersWithRoles]


GET_ORG_USERS = SQLValidator('sqlserver_get_org_users.sql', OrgUsers)


@route(
  'GET',
  '/api/orgs/{org_id}/users',
  match_info=MatchInfo,
  response=OrgUsers,
)
async def get_users_for_org(server: ExampleServer, request: Request[MatchInfo, Empty, Empty]) -> Response[OrgUsers]:
  async with server.pool.acquire() as conn:
    org_users: OrgUsers = await GET_ORG_USERS.fetchrow(conn, request.match_info.org_id)

  return Response(body=org_users)


async def main():  # pragma: nocover
  logging.basicConfig(level=logging.INFO)
  log = logging.getLogger()

  async with create_pool(
    user='postgres',
    host='127.0.0.1',
    database='postgres',
    password='test',
  ) as pool:
    s = ExampleServer(pool)

    add_route(s, s.app.router, get_users_for_org)

    await s.run_app(log, port=8080)


if __name__ == '__main__':  # pragma: nocover
  asyncio.run(main())
