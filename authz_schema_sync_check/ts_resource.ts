/**
 * GENERATED CODE - DO NOT EDIT MANUALLY
 * This file is generated from schema.zed and should not be modified directly.
 */

/**
 * Type representing all valid resource-permission combinations
 * from the SpiceDB schema.
 */
export type ResourcePermission =
  | { resource: "user"; permission: "read" | "update" | "make_admin" | "revoke_admin"; resourceId: string | number }
  | { resource: "group"; permission: "edit_members"; resourceId: string | number }
  | { resource: "organization"; permission: "administrate" | "read"; resourceId: string | number }
;
