import { useState, useEffect } from 'react';
import Header from '../components/Header';
import './Settings.css';

export default function Settings() {
  const [settings, setSettings] = useState({
    autoDispatchSMS: true,
    predictiveAI: true,
    autoRouteUrgent: true,
    darkMode: false,
  });

  const toggleSetting = (key) => {
    setSettings(prev => {
      const newVal = !prev[key];
      
      // If toggling dark mode, apply to body
      if (key === 'darkMode') {
        if (newVal) {
          document.body.classList.add('dark-theme');
        } else {
          document.body.classList.remove('dark-theme');
        }
      }
      
      return { ...prev, [key]: newVal };
    });
  };

  // Check if dark mode is already active on load
  useEffect(() => {
    if (document.body.classList.contains('dark-theme')) {
      setSettings(prev => ({ ...prev, darkMode: true }));
    }
  }, []);

  const ToggleSwitch = ({ checked, onChange }) => (
    <div className={`toggle-switch ${checked ? 'active' : ''}`} onClick={onChange}>
      <div className="toggle-knob"></div>
    </div>
  );

  return (
    <div className="animate-fade-in">
      <Header title="System Settings" subtitle="CONFIGURATION" />
      
      <div className="card settings-container">
        <div className="settings-header">
          <h3 className="text-h2" style={{fontSize: '1.125rem'}}>System Settings</h3>
          <div className="text-muted" style={{fontSize: '0.875rem'}}>Configure coordination & AI behavior</div>
        </div>

        <div className="settings-list">
          
          <div className="setting-item">
            <div className="setting-info">
              <h4>Enable Auto-dispatch SMS</h4>
              <p>Fallback to SMS when WhatsApp delivery fails.</p>
            </div>
            <ToggleSwitch 
              checked={settings.autoDispatchSMS} 
              onChange={() => toggleSetting('autoDispatchSMS')} 
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h4>Use Predictive AI Matching</h4>
              <p>ML ranks donors by reliability + proximity + cooldown.</p>
            </div>
            <ToggleSwitch 
              checked={settings.predictiveAI} 
              onChange={() => toggleSetting('predictiveAI')} 
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h4>Auto-route Urgent Requests</h4>
              <p>Critical cases skip the queue and broadcast instantly.</p>
            </div>
            <ToggleSwitch 
              checked={settings.autoRouteUrgent} 
              onChange={() => toggleSetting('autoRouteUrgent')} 
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <h4>Dark Mode</h4>
              <p>Optimized medical-tech dark theme.</p>
            </div>
            <ToggleSwitch 
              checked={settings.darkMode} 
              onChange={() => toggleSetting('darkMode')} 
            />
          </div>

        </div>
      </div>
    </div>
  );
}
