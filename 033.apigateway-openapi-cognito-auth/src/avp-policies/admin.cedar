permit (
    principal,
    action == App::Action::"POST /admin",
    resource
)
when { principal.custom.role == "admin" };