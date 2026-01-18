permit(
  principal,
  action == App::Action::"/public",
  resource
)
when {
  principal is App::User
  && resource is App::Endpoint
};

