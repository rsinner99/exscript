def execute(scope, user):
    accm    = scope.get('__connection__').get_account_manager()
    account = accm.get_account_from_name(user[0])
    accm.acquire_account(account)
    return 1
