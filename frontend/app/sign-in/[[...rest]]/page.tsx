import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <SignIn
        appearance={{
          variables: {
            colorPrimary: "#6c47ff",
            colorBackground: "#1f2937",
            colorInputBackground: "#111827",
            colorText: "#f9fafb",
            colorTextSecondary: "rgba(255,255,255,0.5)",
            colorInputText: "#f9fafb",
            borderRadius: "8px",
          },
          elements: {
            card: "border border-white/10 shadow-none",
            formButtonPrimary: "bg-[#6c47ff] hover:bg-[#5a38e0]",
          },
        }}
      />
    </div>
  );
}
