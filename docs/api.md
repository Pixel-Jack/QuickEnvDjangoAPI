# API
error_list is a list of string describing why this error occurred.
*... urls are authenticated calls. You should send in the header ```Authorization: token $token``` otherwise it will return a HTTP_401_UNAUTHORIZED.
!... urls are non authenticated calls. You should be anonymous otherwise it will return a HTTP_403_FORBIDDEN, error_list.
\#... urls are admin calls. You should send in the header ```Authorization: token $token``` of an admin user otherwise it will return a HTTP_401_UNAUTHORIZED.
```
admin/  : common admin part of django
auth/   : authentication part and password management
        obtain-token/       : POST  - login (string)
                                    - password (string)
                            return HTTP_200_OK, {"token" : $token }
                            Error HTTP_400_BAD_REQUEST, error_list
        *refresh-token/      : POST    
                            return HTTP_200_OK, {"token" : $token }
                            Error HTTP_400_BAD_REQUEST, error_list
        *delete-token/       : DELETE
                            return {"message", "success"}
                            Error HTTP_400_BAD_REQUEST, error_list
        *change-password/    : POST - email 
                            return HTTP_200_OK
                            Error HTTP_400_BAD_REQUEST, error_list
        reset-password/     : POST  - email 
                            return HTTP_200_OK
                            Error HTTP_400_BAD_REQUEST, error_list
        reset/<pk>/<token>/ : POST  - new_password1
                                    - new_password2
                            return HTTP_200_OK
                            Error HTTP_400_BAD_REQUEST, error_list
user/   : user information management
        !#sign-up/    : POST    - email
                                - username
                                - password
                                - password_confirmation
                    return HTTP_200_OK, {'email': $email, 'username': $username}
                    Error HTTP_400_BAD_REQUEST, error_list
```
