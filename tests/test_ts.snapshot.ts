export type WithDefaultsAndAnnotations = {
  foo: string;
  val: string;
  blah: string;
  fff: string;
};

export type Opt = { key: string; val: null | string };

export type User = {
  user_id: string;
  name: null | string;
  roles: [string];
  options: Record<string, Opt>;
  maybe_options: Record<string, Opt> | null;
  deep_opts: Record<
    string,
    Record<string, Record<string, Record<string, Opt>>>
  >;
  opt_union: null | number | string;
};

export type Org = {
  org_id: string;
  created_at: Date;
  users: [User];
  maybe_users: [User] | null;
};

function getWithDefaultsAndAnnotationsFromWire(
  root: any
): WithDefaultsAndAnnotations {
  return { foo: root.foo, val: root.val, blah: root.blah, fff: root.fff };
}

function getOptFromWire(root: any): Opt {
  return { key: root.key, val: root.val };
}

function getUserFromWire(root: any): User {
  return {
    user_id: root.user_id,
    name: root.name,
    roles: root.roles,
    options: Object.fromEntries(
      Object.entries(root.options as Record<string, Opt>).map(([k1, v1]) => {
        return [k1, getOptFromWire(v1)];
      })
    ),
    maybe_options:
      root.maybe_options === null
        ? null
        : Object.fromEntries(
            Object.entries(root.maybe_options as Record<string, Opt>).map(
              ([k2, v2]) => {
                return [k2, getOptFromWire(v2)];
              }
            )
          ),
    deep_opts: Object.fromEntries(
      Object.entries(
        root.deep_opts as Record<
          string,
          Record<string, Record<string, Record<string, Opt>>>
        >
      ).map(([k1, v1]) => {
        return [
          k1,
          Object.fromEntries(
            Object.entries(
              v1 as Record<string, Record<string, Record<string, Opt>>>
            ).map(([k2, v2]) => {
              return [
                k2,
                Object.fromEntries(
                  Object.entries(v2 as Record<string, Record<string, Opt>>).map(
                    ([k3, v3]) => {
                      return [
                        k3,
                        Object.fromEntries(
                          Object.entries(v3 as Record<string, Opt>).map(
                            ([k4, v4]) => {
                              return [k4, getOptFromWire(v4)];
                            }
                          )
                        ),
                      ];
                    }
                  )
                ),
              ];
            })
          ),
        ];
      })
    ),
    opt_union: root.opt_union,
  };
}

function getOrgFromWire(root: any): Org {
  return {
    org_id: root.org_id,
    created_at: new Date(root.created_at * 1000),
    users: root.users.map((v1: User) => {
      return getUserFromWire(v1);
    }),
    maybe_users:
      root.maybe_users === null
        ? null
        : root.maybe_users.map((v2: User) => {
            return getUserFromWire(v2);
          }),
  };
}

function convertWithDefaultsAndAnnotationsToWire(
  root: any
): WithDefaultsAndAnnotations {
  return { foo: root.foo, val: root.val, blah: root.blah, fff: root.fff };
}

function convertOptToWire(root: any): Opt {
  return { key: root.key, val: root.val };
}

function convertUserToWire(root: any): User {
  return {
    user_id: root.user_id,
    name: root.name,
    roles: root.roles.map((v1: string) => {
      return v1;
    }),
    options: Object.fromEntries(
      Object.entries(root.options as Record<string, Opt>).map(([k1, v1]) => {
        return [k1, convertOptToWire(v1)];
      })
    ),
    maybe_options:
      root.maybe_options === null
        ? null
        : Object.fromEntries(
            Object.entries(root.maybe_options as Record<string, Opt>).map(
              ([k2, v2]) => {
                return [k2, convertOptToWire(v2)];
              }
            )
          ),
    deep_opts: Object.fromEntries(
      Object.entries(
        root.deep_opts as Record<
          string,
          Record<string, Record<string, Record<string, Opt>>>
        >
      ).map(([k1, v1]) => {
        return [
          k1,
          Object.fromEntries(
            Object.entries(
              v1 as Record<string, Record<string, Record<string, Opt>>>
            ).map(([k2, v2]) => {
              return [
                k2,
                Object.fromEntries(
                  Object.entries(v2 as Record<string, Record<string, Opt>>).map(
                    ([k3, v3]) => {
                      return [
                        k3,
                        Object.fromEntries(
                          Object.entries(v3 as Record<string, Opt>).map(
                            ([k4, v4]) => {
                              return [k4, convertOptToWire(v4)];
                            }
                          )
                        ),
                      ];
                    }
                  )
                ),
              ];
            })
          ),
        ];
      })
    ),
    opt_union: root.opt_union,
  };
}

function convertOrgToWire(root: any): Org {
  return {
    org_id: root.org_id,
    created_at: root.created_at.getTime(),
    users: root.users.map((v1: User) => {
      return convertUserToWire(v1);
    }),
    maybe_users:
      root.maybe_users === null
        ? null
        : root.maybe_users.map((v2: User) => {
            return convertUserToWire(v2);
          }),
  };
}
