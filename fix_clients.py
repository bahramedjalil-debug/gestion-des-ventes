from api.models import Client, User

for client in Client.objects.filter(user__isnull=True):
    print("Fixing:", client.name)

    user = User.objects.filter(username__icontains=client.name.split()[0]).first()

    if user:
        client.user = user
        client.save()
        print("  → linked to", user.username)
    else:
        print("  → NO USER FOUND")