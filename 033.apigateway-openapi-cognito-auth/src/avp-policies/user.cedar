permit (
    principal,
    action == App::Action::"/user",
    resource
)
when { principal.role == "user" };

