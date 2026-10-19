"use client";
import { supabase } from "@/lib/supabase";
export default function Signup() {
  async function onSubmit(e: any) {
    const email = e.target.email.value;
    console.log("signup", email, e.target.password.value);
    await supabase.auth.signUp({ email, password: e.target.password.value });
  }
  return (
    <form onSubmit={onSubmit}>
      <input type="email" name="email" placeholder="Email" />
      <input type="password" name="password" placeholder="Password" />
      <input name="phone_number" placeholder="Phone" />
      <input name="date_of_birth" placeholder="Birthday" />
      <label><input type="checkbox" defaultChecked /> Send me marketing newsletter</label>
      <button>Sign up</button>
      <a href="#">No thanks, I don't want to save money</a>
    </form>
  );
}
