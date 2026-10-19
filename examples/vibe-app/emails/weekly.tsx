import { Resend } from "resend";
const resend = new Resend(process.env.RESEND_API_KEY);
export async function sendWeekly(to: string) {
  await resend.emails.send({ from: "news@vibe.app", to, subject: "This week", html: "<p>New features!</p>" });
}
