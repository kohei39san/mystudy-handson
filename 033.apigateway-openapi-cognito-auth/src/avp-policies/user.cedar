permit (
    principal,
    action == App::Action::"GET /user",
    resource
)
when { principal.custom.role == "user" };

