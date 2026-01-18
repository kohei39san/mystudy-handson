permit(
  principal,
  action == App::Action::"GET /public",
  resource
)
when {
  principal is App::User
  && resource is App::Endpoint
};