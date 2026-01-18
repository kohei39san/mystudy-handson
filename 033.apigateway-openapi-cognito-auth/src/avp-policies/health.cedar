permit(
  principal,
  action == App::Action::"GET /health",
  resource
)
when {
  principal is App::User
  && resource is App::Endpoint
};

