import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/register", "/auth/callback"];
const PENDING_PATHS = ["/pending-approval"];

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some(
    (path) => pathname === path || (path !== "/" && pathname.startsWith(`${path}/`)),
  );
}

function isPendingPath(pathname: string): boolean {
  return PENDING_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

function loginRedirectUrl(request: NextRequest): URL {
  const loginUrl = new URL("/login", request.url);
  const redirectTarget = `${request.nextUrl.pathname}${request.nextUrl.search}`;
  loginUrl.searchParams.set("redirect", redirectTarget);
  return loginUrl;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("estateos-access")?.value;

  if (pathname.startsWith("/_next") || pathname.startsWith("/api") || pathname.includes(".")) {
    return NextResponse.next();
  }

  if (!token && isPendingPath(pathname)) {
    return NextResponse.redirect(loginRedirectUrl(request));
  }

  if (!token && !isPublicPath(pathname)) {
    return NextResponse.redirect(loginRedirectUrl(request));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
