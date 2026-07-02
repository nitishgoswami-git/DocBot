import ChatArea from "./components/ChatArea";
import Upload from "./components/upload";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 min-h-0">
        <div className="flex flex-1 min-h-0 max-w-lg flex-col bg-white ">
          <Upload />
        </div>

        <div className="flex flex-1 min-h-0  text-white">
          <ChatArea />
        </div>
      </main>
    </div>
  );
}