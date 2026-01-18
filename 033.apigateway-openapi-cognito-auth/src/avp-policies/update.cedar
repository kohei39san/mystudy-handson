permit(
  principal,
  action == App::Action::"/update",
  resource
)
when {
  principal is App::User
  && resource is App::Endpoint
  && principal.role == "user" || principal.role == "admin"
};