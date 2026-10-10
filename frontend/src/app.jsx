import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import RegulatorySearch from "./pages/RegulatorySearch.jsx";
import WhatsNew from "./pages/WhatsNew.jsx";
import RuleEngine from "./pages/RuleEngine.jsx";
import DocumentLibrary from "./pages/DocumentLibrary.jsx";
import TradeValidator from "./pages/TradeValidator.jsx";
import Alerts from "./pages/Alerts.jsx";
import Reports from "./pages/Reports.jsx";
import ImpactAnalysis from "./pages/ImpactAnalysis.jsx";
import Placeholder from "./pages/Placeholder.jsx";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<RegulatorySearch />} />
        <Route path="/updates" element={<WhatsNew />} />
        <Route path="/rule-engine" element={<RuleEngine />} />
        <Route path="/library" element={<DocumentLibrary />} />
        <Route path="/validator" element={<TradeValidator />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/impact" element={<ImpactAnalysis />} />
        <Route path="*" element={<Placeholder />} />
      </Routes>
    </Layout>
  );
}
