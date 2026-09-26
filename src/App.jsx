import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/common/PrivateRoute';

// Public pages
import LandingPage  from './pages/LandingPage';
import LoginPage    from './pages/LoginPage';
import SignupPage   from './pages/SignupPage';

// Dashboard layout + pages
import DashboardLayout        from './components/layout/DashboardLayout';
import DashboardHome          from './pages/dashboard/DashboardHome';
import RegionalTwinsPage      from './pages/dashboard/RegionalTwinsPage';
import SegmentTwinsPage       from './pages/dashboard/SegmentTwinsPage';
import CampaignGeneratorPage  from './pages/dashboard/CampaignGeneratorPage';
import SimulationPage         from './pages/dashboard/SimulationPage';
import SellerIntelligencePage from './pages/dashboard/SellerIntelligencePage';
import AnalyticsPage          from './pages/dashboard/AnalyticsPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* ── Public routes ── */}
          <Route path="/"       element={<LandingPage />} />
          <Route path="/login"  element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* ── Protected dashboard routes ── */}
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <DashboardLayout />
              </PrivateRoute>
            }
          >
            <Route index                    element={<DashboardHome />} />
            <Route path="regional-twins"    element={<RegionalTwinsPage />} />
            <Route path="segment-twins"     element={<SegmentTwinsPage />} />
            <Route path="campaigns"         element={<CampaignGeneratorPage />} />
            <Route path="simulation"        element={<SimulationPage />} />
            <Route path="seller-intel"      element={<SellerIntelligencePage />} />
            <Route path="analytics"         element={<AnalyticsPage />} />
            {/* Fallback inside dashboard */}
            <Route path="*"                 element={<Navigate to="/dashboard" replace />} />
          </Route>

          {/* ── Global fallback ── */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
