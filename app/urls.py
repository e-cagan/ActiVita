from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("change_password", views.change_password, name="change_password"),
    path("create_event", views.create_event, name="create_event"),
    path("edit_event/<int:event_id>", views.edit_event, name="edit_event"),
    path("delete_event/<int:event_id>", views.delete_event, name="delete_event"),
    path("event_details/<int:event_id>", views.event_details, name="event_details"),
    path("participate_event/<int:event_id>", views.participate_event, name="participate_event"),
    path("departicipate_event/<int:event_id>", views.departicipate_event, name="departicipate_event"),
    path("make_donation/<int:event_id>", views.make_donation, name="make_donation"),
    path("search", views.search, name="search"),
    path("profile_page", views.profile_page, name="profile_page"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("delete_profile", views.delete_profile, name="delete_profile"),
    path("view_notifications", views.view_notifications, name="view_notifications"),
    path("congratulate/<int:congratulator_id>/<int:user_id>", views.congratulate, name="congratulate"),
    path("notify_participation/<int:event_id>/<int:participator_id>", views.notify_participation, name="notify_participation"),
    path('mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('read_all', views.read_all, name='read_all'),
]
