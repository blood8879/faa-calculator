"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo/Title */}
        <Link
          href="/"
          className="flex items-center space-x-2 transition-opacity hover:opacity-80"
        >
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <span className="text-lg font-bold">F</span>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-semibold leading-tight">
                FAA Strategy Calculator
              </span>
            </div>
          </div>
        </Link>

        {/* Navigation Tabs - Desktop */}
        <nav className="hidden md:flex">
          <Tabs value={pathname} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <Link href="/" passHref legacyBehavior>
                <TabsTrigger
                  value="/"
                  className={cn(
                    "cursor-pointer",
                    pathname === "/" && "data-[state=active]:bg-background"
                  )}
                >
                  Calculator
                </TabsTrigger>
              </Link>
              <Link href="/backtest" passHref legacyBehavior>
                <TabsTrigger
                  value="/backtest"
                  className={cn(
                    "cursor-pointer",
                    pathname === "/backtest" &&
                      "data-[state=active]:bg-background"
                  )}
                >
                  Backtest
                </TabsTrigger>
              </Link>
            </TabsList>
          </Tabs>
        </nav>

        {/* Mobile Navigation */}
        <nav className="flex md:hidden">
          <div className="flex gap-2">
            <Link
              href="/"
              className={cn(
                "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                pathname === "/"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              Calculator
            </Link>
            <Link
              href="/backtest"
              className={cn(
                "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                pathname === "/backtest"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              Backtest
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}
