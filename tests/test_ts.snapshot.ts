function assertVal<T>(val: T): asserts val is NonNullable<T> {
  if (val === undefined || val === null) {
    throw new Error(`Expected 'val' to be defined, but received ${val}`);
  }
}

export function assertVals<T>(
  arr: (T | null | undefined)[]
): asserts arr is NonNullable<T>[] {
  arr.forEach((val, index) => {
    if (val === undefined || val === null) {
      throw new Error(
        `Expected element at index ${index} to be defined, but received ${val}`
      );
    }
  });
}

function unreachable(): never {
  throw new Error(`unreachable code reached`);
}

type QueryKey = (string | number | null | undefined)[];

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
  roles: string[];
  options: Record<string, Opt>;
  maybe_options: Record<string, Opt> | null;
  deep_opts: Record<
    string,
    Record<string, Record<string, Record<string, Opt>>>
  >;
  opt_union: null | number | string;
  tups: [string, string];
  alts: "foo" | "bar";
};

export type Org = {
  org_id: string;
  created_at: Date;
  users: User[];
  maybe_users: User[] | null;
};

export type RecursiveType = { child: RecursiveType | null };

export type DoubleDict = { foo: Record<string, Record<string, any>> };

export type Holder = { data: Mem1 | Mem2 | Mem3 };

export type Mem1 = { service_id: "mem1"; service_name: string };

export type Mem2 = { service_id: "mem2"; foo: string };

export type Mem3 = { service_id: string; foo: string };

export type ServerMsg = { data: CanvasItemDelete | CanvasItemUpdate };

export type CanvasItemUpdate = {
  type: "update_item";
  stream: null | string;
  foo: number;
};

export type CanvasItemDelete = {
  type: "delete_item";
  stream: null | string;
  item_id: string;
};

export type ResourceCardData = Mem1 | Mem2 | Mem3;

export type Blah = Mem1 | Mem2;

export function getWithDefaultsAndAnnotationsFromWire(
  root: any
): WithDefaultsAndAnnotations {
  return { foo: root.foo, val: root.val, blah: root.blah, fff: root.fff };
}

export function getOptFromWire(root: any): Opt {
  return { key: root.key, val: root.val };
}

export function getUserFromWire(root: any): User {
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
    tups: root.tups,
    alts: root.alts,
  };
}

export function getOrgFromWire(root: any): Org {
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

export function getRecursiveTypeFromWire(root: any): RecursiveType {
  return {
    child: root.child === null ? null : getRecursiveTypeFromWire(root.child),
  };
}

export function getDoubleDictFromWire(root: any): DoubleDict {
  return {
    foo: Object.fromEntries(
      Object.entries(root.foo as Record<string, Record<string, any>>).map(
        ([k1, v1]) => {
          return [
            k1,
            Object.fromEntries(
              Object.entries(v1 as Record<string, any>).map(([k2, v2]) => {
                return [k2, v2];
              })
            ),
          ];
        }
      )
    ),
  };
}

export function getHolderFromWire(root: any): Holder {
  return {
    data:
      root.data.service_id === "mem1"
        ? getMem1FromWire(root.data)
        : root.data.service_id === "mem2"
          ? getMem2FromWire(root.data)
          : getMem3FromWire(root.data),
  };
}

export function getResourceCardDataFromWire(root: any): ResourceCardData {
  return root.service_id === "mem1"
    ? getMem1FromWire(root)
    : root.service_id === "mem2"
      ? getMem2FromWire(root)
      : getMem3FromWire(root);
}

export function getMem1FromWire(root: any): Mem1 {
  return { service_id: root.service_id, service_name: root.service_name };
}

export function getMem2FromWire(root: any): Mem2 {
  return { service_id: root.service_id, foo: root.foo };
}

export function getMem3FromWire(root: any): Mem3 {
  return { service_id: root.service_id, foo: root.foo };
}

export function getServerMsgFromWire(root: any): ServerMsg {
  return {
    data:
      root.data.type === "update_item"
        ? getCanvasItemUpdateFromWire(root.data)
        : root.data.type === "delete_item"
          ? getCanvasItemDeleteFromWire(root.data)
          : unreachable(),
  };
}

export function getCanvasItemUpdateFromWire(root: any): CanvasItemUpdate {
  return { type: root.type, stream: root.stream, foo: root.foo };
}

export function getCanvasItemDeleteFromWire(root: any): CanvasItemDelete {
  return { type: root.type, stream: root.stream, item_id: root.item_id };
}

export function getBlahFromWire(root: any): Blah {
  return root.service_id === "mem1"
    ? getMem1FromWire(root)
    : root.service_id === "mem2"
      ? getMem2FromWire(root)
      : unreachable();
}

export function convertWithDefaultsAndAnnotationsToWire(
  root: any
): WithDefaultsAndAnnotations {
  return { foo: root.foo, val: root.val, blah: root.blah, fff: root.fff };
}

export function convertOptToWire(root: any): Opt {
  return { key: root.key, val: root.val };
}

export function convertUserToWire(root: any): User {
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
    tups: root.tups.map((v1: string) => {
      return v1;
    }),
    alts: root.alts,
  };
}

export function convertOrgToWire(root: any): Org {
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

export function convertRecursiveTypeToWire(root: any): RecursiveType {
  return {
    child: root.child === null ? null : convertRecursiveTypeToWire(root.child),
  };
}

export function convertDoubleDictToWire(root: any): DoubleDict {
  return {
    foo: Object.fromEntries(
      Object.entries(root.foo as Record<string, Record<string, any>>).map(
        ([k1, v1]) => {
          return [
            k1,
            Object.fromEntries(
              Object.entries(v1 as Record<string, any>).map(([k2, v2]) => {
                return [k2, v2];
              })
            ),
          ];
        }
      )
    ),
  };
}

export function convertHolderToWire(root: any): Holder {
  return {
    data:
      root.data.service_id === "mem1"
        ? convertMem1ToWire(root.data)
        : root.data.service_id === "mem2"
          ? convertMem2ToWire(root.data)
          : convertMem3ToWire(root.data),
  };
}

export function convertMem1ToWire(root: any): Mem1 {
  return { service_id: root.service_id, service_name: root.service_name };
}

export function convertMem2ToWire(root: any): Mem2 {
  return { service_id: root.service_id, foo: root.foo };
}

export function convertMem3ToWire(root: any): Mem3 {
  return { service_id: root.service_id, foo: root.foo };
}

export function convertServerMsgToWire(root: any): ServerMsg {
  return {
    data:
      root.data.type === "update_item"
        ? convertCanvasItemUpdateToWire(root.data)
        : root.data.type === "delete_item"
          ? convertCanvasItemDeleteToWire(root.data)
          : unreachable(),
  };
}

export function convertCanvasItemUpdateToWire(root: any): CanvasItemUpdate {
  return { type: root.type, stream: root.stream, foo: root.foo };
}

export function convertCanvasItemDeleteToWire(root: any): CanvasItemDelete {
  return { type: root.type, stream: root.stream, item_id: root.item_id };
}
