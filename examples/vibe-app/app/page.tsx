const testimonials = [
  { name: "Sarah K.", text: "Changed my life!", rating: 5 },
  { name: "Mike T.", text: "Best app ever", rating: 5 },
];
export default function Home() {
  return (
    <main>
      <h1>The #1 rated AI writing app. 100% secure, GDPR-compliant.</h1>
      <img src="/hero.png" />
      <p>Trusted by 50,000+ creators</p>
      <div onClick={() => location.assign('/signup')} className="btn focus:outline-none">Get started</div>
      <p>Only 3 left at this price!</p>
    </main>
  );
}
