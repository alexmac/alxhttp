with
  org_users as (
    select
      u.*
    , row_to_json(ga.*) as google
    from
      usermodel.user_org uo
      join usermodel.users u on uo.user_id = u.user_id
      left join usermodel.user_google ug on ug.user_id = u.user_id
      left join usermodel.google_account ga on ga.sub = ug.sub
    where
      uo.org_id = $1
  )
, user_roles as (
    select
      uo.user_id
    , array_agg(r.role) as roles
    from
      usermodel.user_org uo
      join usermodel.roles r on uo.role = r.role
    where
      uo.org_id = $1
    group by
      uo.user_id
  )
, combined as (
    select
      ou.*
    , array_to_json(coalesce(ur.roles, array[]::text[])) as roles
    from
      org_users ou
      left join user_roles ur on ou.user_id = ur.user_id
  )
select
  $1                                as org_id
, json_agg(row_to_json(combined.*)) as users
from
  combined;