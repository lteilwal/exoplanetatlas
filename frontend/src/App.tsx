import React, { useEffect, useState } from "react";
import { Footer } from "./components/Footer";
import { Navbar } from "./components/Navbar";
import { CatalogPage } from "./pages/CatalogPage";
import { ComparePage } from "./pages/ComparePage";
import { ExplorePage } from "./pages/ExplorePage";
import { PlanetDetailPage } from "./pages/PlanetDetailPage";
import { SystemDetailPage } from "./pages/SystemDetailPage";
import { SystemsListPage } from "./pages/SystemsListPage";
import { PlanetSummary } from "./types";

export const App: React.FC = () => {
  // Navigation state
  const [currentTab, setCurrentTab] = useState<string>("catalog");
  const [selectedPlanetName, setSelectedPlanetName] = useState<string | null>(null);
  const [selectedSystemName, setSelectedSystemName] = useState<string | null>(null);

  // Compare basket (up to 4 planets)
  const [comparedPlanets, setComparedPlanets] = useState<PlanetSummary[]>(() => {
    try {
      const saved = localStorage.getItem("exoplanet_atlas_compare");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Save compare list to localStorage
  useEffect(() => {
    try {
      localStorage.setItem("exoplanet_atlas_compare", JSON.stringify(comparedPlanets));
    } catch (e) {
      console.error(e);
    }
  }, [comparedPlanets]);

  // URL Hash Synchronizer for bookmarking and history
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash.startsWith("planet/")) {
        const name = decodeURIComponent(hash.replace("planet/", ""));
        setSelectedPlanetName(name);
        setCurrentTab("planet");
      } else if (hash.startsWith("system/")) {
        const name = decodeURIComponent(hash.replace("system/", ""));
        setSelectedSystemName(name);
        setCurrentTab("system");
      } else if (hash === "compare") {
        setCurrentTab("compare");
      } else if (hash === "explore") {
        setCurrentTab("explore");
      } else if (hash === "systems") {
        setCurrentTab("systems");
      } else {
        setCurrentTab("catalog");
      }
    };

    window.addEventListener("hashchange", handleHashChange);
    handleHashChange(); // Handle initial load

    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (tab: string, param?: string) => {
    if (tab === "planet" && param) {
      window.location.hash = `planet/${encodeURIComponent(param)}`;
    } else if (tab === "system" && param) {
      window.location.hash = `system/${encodeURIComponent(param)}`;
    } else if (tab === "compare") {
      window.location.hash = "compare";
    } else if (tab === "explore") {
      window.location.hash = "explore";
    } else if (tab === "systems") {
      window.location.hash = "systems";
    } else {
      window.location.hash = "";
      setCurrentTab("catalog");
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleToggleCompare = (planet: PlanetSummary) => {
    setComparedPlanets((prev) => {
      const exists = prev.some((p) => p.name === planet.name);
      if (exists) {
        return prev.filter((p) => p.name !== planet.name);
      }
      if (prev.length >= 4) {
        alert("Comparison matrix accommodates up to 4 targets simultaneously.");
        return prev;
      }
      return [...prev, planet];
    });
  };

  const handleRemoveCompare = (planetName: string) => {
    setComparedPlanets((prev) => prev.filter((p) => p.name !== planetName));
  };

  const handleClearCompare = () => {
    setComparedPlanets([]);
  };

  return (
    <div className="app-container">
      <div>
        {/* Navigation Bar */}
        <Navbar
          currentTab={currentTab}
          onNavigate={navigate}
          compareCount={comparedPlanets.length}
        />

        {/* Dynamic Page Views */}
        <main>
          {currentTab === "catalog" && (
            <CatalogPage
              onSelectPlanet={(name) => navigate("planet", name)}
              comparedPlanets={comparedPlanets}
              onToggleCompare={handleToggleCompare}
            />
          )}

          {currentTab === "systems" && (
            <SystemsListPage
              onSelectSystem={(name) => navigate("system", name)}
            />
          )}

          {currentTab === "planet" && selectedPlanetName && (
            <PlanetDetailPage
              planetName={selectedPlanetName}
              onBack={() => navigate("catalog")}
              onNavigateSystem={(sysName) => navigate("system", sysName)}
              onToggleCompare={handleToggleCompare}
              isCompared={comparedPlanets.some((p) => p.name === selectedPlanetName)}
            />
          )}

          {currentTab === "system" && selectedSystemName && (
            <SystemDetailPage
              systemName={selectedSystemName}
              onBack={() => navigate("systems")}
              onSelectPlanet={(name) => navigate("planet", name)}
              onToggleCompare={handleToggleCompare}
              comparedPlanets={comparedPlanets}
            />
          )}

          {currentTab === "compare" && (
            <ComparePage
              comparedPlanets={comparedPlanets}
              onRemovePlanet={handleRemoveCompare}
              onClearAll={handleClearCompare}
              onSelectPlanet={(name) => navigate("planet", name)}
              onNavigateExplore={() => navigate("catalog")}
            />
          )}

          {currentTab === "explore" && (
            <ExplorePage
              onSelectPlanet={(name) => navigate("planet", name)}
            />
          )}
        </main>
      </div>

      {/* Global Footer */}
      <Footer />
    </div>
  );
};
export default App;
