permit (
    principal,
    action == App::Action::"/admin",
    resource
)
when { principal.role == "admin" };