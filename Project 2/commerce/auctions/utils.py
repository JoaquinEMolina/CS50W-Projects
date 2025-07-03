
def is_in_watchlist(user,listing):
    return user in listing.watchlist.all()