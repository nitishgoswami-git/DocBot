"use client";

import { useState } from "react";
import axios from "axios";
import type { AxiosRequestConfig, AxiosResponse, AxiosError } from "axios";

import { ClipLoader } from "react-spinners";
import { useAuth } from "@clerk/nextjs";

type Post = {
  userId: number;
  id: number;
  title: string;
  body: string;
};

export default function Upload() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [res, setRes] = useState<string[]>([]);
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);
  const { userId } = useAuth();
  const [sessionId] = useState(() => crypto.randomUUID());

  const handleFile = async (selectedFile: File | null) => {
    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      alert("Please upload a PDF file.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      alert("File size must be less than 10MB.");
      return;
    }

    setFile(selectedFile);
    setRes([]);
    setIsError(false);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("user_id", userId ?? "");
      formData.append("SESSIONID", sessionId);

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const { job_id, status } = await response.json();
      setRes((prev) => [...prev, status]);

      const es = new EventSource(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/upload/progress/${job_id}`,
      );

      es.addEventListener("progress", (event) => {
        const data = JSON.parse(event.data);

        setRes((prev) => [...prev, data.status]);
      });

      es.addEventListener("complete", (event) => {
        const data = JSON.parse(event.data);
        console.log("Complete");

        setRes((prev) => [...prev, data.status]);

        setLoading(false);
        es.close();
      });

      es.onerror = () => {
        setLoading(false);
        setIsError(true);

        setRes((prev) => [...prev, "Connection lost while processing PDF"]);

        console.log("Error");
        es.close();
      };
    } catch (error) {
      setLoading(false);
      setIsError(true);
      setRes(["Upload Failed"]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files?.[0];
    handleFile(droppedFile);
  };

  return (
    <div className="flex-1 min-h-0 w-full">
      <label className="block h-full w-full cursor-pointer">
        <div
          onDragEnter={() => setIsDragging(true)}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={(e) => {
            if (e.currentTarget === e.target) {
              setIsDragging(false);
            }
          }}
          onDrop={handleDrop}
          className={`flex h-full min-h-[400px] flex-col items-center justify-center  border-2 border-dashed p-8 text-center transition-all duration-200 ${
            isDragging
              ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-zinc-800"
              : "border-zinc-300 bg-white hover:border-blue-500 hover:bg-blue-50 dark:border-zinc-700 dark:bg-zinc-900 dark:hover:border-blue-400 dark:hover:bg-zinc-800"
          }`}
        >
          {res.length > 0 && (
            <div
              className={`flex mb-6 mt-6 rounded-lg  px-4 py-2 text-sm font-medium 
                `}
            >
              <div
                className={`mb-6 mt-6 rounded-lg border px-4 py-2 text-sm font-medium ${
                  isError ? " text-red-700" : " text-green-700"
                }`}
              >
                {loading && <ClipLoader color="white" className="m-5" />}

                {res.map((item, index) => (
                  <div key={index}>
                    {isError ? "x" : ">"} {item}
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
            <svg
              className="h-8 w-8 text-blue-600 dark:text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 16V4m0 0l-4 4m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"
              />
            </svg>
          </div>

          <h2 className="text-xl font-semibold text-zinc-900 dark:text-white">
            Upload your PDF
          </h2>

          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
            Drag & drop a PDF here or click anywhere to browse
          </p>

          {file && (
            <div className="mt-6 rounded-lg border border-green-200 bg-green-50 px-4 py-2 text-sm font-medium text-green-700 dark:border-green-800 dark:bg-green-900/20 dark:text-green-400">
              📄 {file.name}
            </div>
          )}

          <p className="mt-4 text-xs text-zinc-400">
            PDF only • Maximum file size: 10MB
          </p>

          <input
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
          />
        </div>
      </label>
    </div>
  );
}
