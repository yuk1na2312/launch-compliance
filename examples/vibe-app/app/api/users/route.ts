import Stripe from "stripe";
import OpenAI from "openai";
import { createClient } from "@supabase/supabase-js";
const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY!);
const stripe = new Stripe(process.env.STRIPE_KEY!);
export async function GET(req: Request) {
  const id = new URL(req.url).searchParams.get("id");
  const { data } = await supabase.from("profiles").select("*").eq("id", id);
  return Response.json(data);
}
export async function POST(req: Request) {
  const body = await req.json();
  const session = await stripe.checkout.sessions.create({ mode: "subscription", line_items: [] });
  const ai = new OpenAI();
  await ai.chat.completions.create({ model: "gpt-4o", messages: [{ role: "user", content: body.notes }] });
  return Response.json({ url: session.url });
}
