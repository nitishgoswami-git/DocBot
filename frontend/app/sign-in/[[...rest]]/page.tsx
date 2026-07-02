import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <SignIn
        appearance={{
          variables: {
            colorPrimary: "#6c47ff",
            colorBackground: "#1f2937",
            colorInput: "#111827", // Fixes the exact build error
            colorForeground: "#f9fafb", // Replaces colorText
            colorMutedForeground: "rgba(255,255,255,0.5)", // Replaces colorTextSecondary
            colorInputForeground: "#f9fafb", // Replaces colorInputText
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
