insert into
  usermodel.orgs (org_name)
values
  ($1)
returning
  *