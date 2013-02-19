default_attributes(
  "authorization" => {
    "sudo" => {
      "groups" => ["admin", "wheel", "sysadmin"],
      "users" => ["vagrant", "slok"],
      "passwordless" => true
    }
  }
)