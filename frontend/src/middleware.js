import { defineMiddleware } from "astro/middleware";

const BASE_URL = "http://localhost:4321";

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.url);

  if (protectedRoute(url.pathname)) {

    const redirectUrl = `${BASE_URL}/login`;

    const cookies = context.request.headers.get('cookie');
    if(!cookies) {
        return redirectToLogin(BASE_URL);
    }

    const accessTokenCookie = cookies.split('; ').find(row => row.startsWith('access_token_cookie='))?.split('=')[1];

    try {
      const response = await fetch('http://localhost:5000/protected', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          //Añadir la cookie del cliente en la petición al backend para ver si está autenticado
          'Cookie': `access_token_cookie=${accessTokenCookie}`,
        },
      });

      if (response.ok) {
        return next();
      } else {
        return redirectToLogin(BASE_URL);
      }
    } catch (error) {
      console.error("Error fetching protected resource:", error);
      return new Response("Error", { status: 500 });
    }
  } else {
    //Si no es una ruta protegida, continuar
    return next();
  }
});

const protectedRoute = (route) => {
    if(route === "/home" || route === "/" || route === "/personal") {
        return true;
    }else{
        return false;
    }
}
const redirectToLogin = (BASE_URL) => {
    return Response.redirect(`${BASE_URL}/login`, 302);
}