permit(
  principal,
  action == App::Action::"PATCH /update",
  resource
)
when {
  principal is App::User
  && (principal.custom.role == "user" || principal.custom.role == "admin")
};