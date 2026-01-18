permit(
  principal,
  action == App::Action::"/health",
  resource
)
when {
  principal is App::User
  && resource is App::Endpoint
};

