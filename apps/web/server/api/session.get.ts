export default defineEventHandler((event) => ({
  signedIn: Boolean(event.context.logtoUser),
  subject: event.context.logtoUser?.sub,
}))
