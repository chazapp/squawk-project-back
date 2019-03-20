package squawk.requests;

import javax.validation.constraints.NotNull;

public class Authentication {
    @NotNull
    private String email;

    @NotNull
    private String password;
}
