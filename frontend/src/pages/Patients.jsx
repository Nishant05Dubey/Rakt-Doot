import { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Search, Filter, Plus, X } from 'lucide-react';
import './Patients.css';

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    patient_name: '', blood_type: 'O+', hospital: '', city: '', urgency: 'Urgent'
  });

  const fetchPatients = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      if (!apiUrl) throw new Error("API URL missing");
      const res = await fetch(`${apiUrl}/admin/dashboard`);
      if (res.ok) {
        const data = await res.json();
        setPatients(data.patient_queue || []);
      }
    } catch (e) {
      console.error(e);
      // Fallback data
      setPatients([
        { request_id: 'RD-001', patient_name: 'Aryan Mehta', blood_type: 'O+', hospital: 'Apollo Hospital', city: 'Hyderabad', status: 'Searching', created_at: '2026-04-12' },
        { request_id: 'RD-002', patient_name: 'Priya Sharma', blood_type: 'B-', hospital: 'AIIMS', city: 'Delhi', status: 'Searching', created_at: '2026-04-20' },
        { request_id: 'RD-003', patient_name: 'Rohan Das', blood_type: 'AB+', hospital: 'Ruby Hall', city: 'Pune', status: 'Confirmed', created_at: '2026-03-28' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleAddPatient = async (e) => {
    e.preventDefault();
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      const res = await fetch(`${apiUrl}/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setIsModalOpen(false);
        fetchPatients();
      }
    } catch (err) {
      console.error(err);
      // Local optimistic update if API fails
      setPatients([{ request_id: `RD-${Math.random().toString().substring(2,6)}`, ...formData, status: 'Searching', created_at: new Date().toISOString() }, ...patients]);
      setIsModalOpen(false);
    }
  };

  const renderStatusBadge = (status) => {
    if (status === 'Confirmed') return <span className="badge badge-scheduled">● Confirmed</span>;
    if (status === 'Searching') return <span className="badge badge-urgent">● Searching</span>;
    return <span className="badge badge-critical">● {status}</span>;
  };

  return (
    <div className="animate-fade-in">
      <Header title="Thalassemia Patients" subtitle="PATIENT REGISTRY" />

      <div className="card controls-bar">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input type="text" placeholder="Search by name or hospital..." className="search-input" />
        </div>
        
        <div className="filters">
          <select className="filter-select">
            <option>All Blood Groups</option>
            <option>O+</option><option>O-</option><option>A+</option><option>A-</option>
            <option>B+</option><option>B-</option><option>AB+</option><option>AB-</option>
          </select>
          <select className="filter-select">
            <option>All Statuses</option>
            <option>Searching</option>
            <option>Confirmed</option>
          </select>
          <button className="btn-primary" onClick={() => setIsModalOpen(true)}>
            <Plus size={16} /> Add Patient
          </button>
        </div>
      </div>

      <div className="card queue-section">
        <div className="queue-header">
          <h3 className="text-h2" style={{fontSize: '1.125rem'}}>Thalassemia Patients</h3>
          <span className="case-count">{patients.length} records</span>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>PATIENT NAME</th>
                <th>BLOOD</th>
                <th>HOSPITAL / CITY</th>
                <th>DATE ADDED</th>
                <th className="text-right">AI MATCH STATUS</th>
              </tr>
            </thead>
            <tbody>
              {loading ? <tr><td colSpan="5" className="text-center" style={{padding: '2rem'}}>Loading...</td></tr> : 
                patients.map((patient) => (
                <tr key={patient.request_id}>
                  <td>
                    <div className="patient-name">{patient.patient_name}</div>
                    <div className="patient-id">{patient.request_id}</div>
                  </td>
                  <td><span className="blood-badge">{patient.blood_type}</span></td>
                  <td>
                    <div>{patient.hospital}</div>
                    <div className="text-muted">{patient.city}</div>
                  </td>
                  <td>{new Date(patient.created_at).toLocaleDateString()}</td>
                  <td className="text-right">{renderStatusBadge(patient.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className="modal-overlay animate-fade-in">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Register New Patient</h3>
              <button className="close-btn" onClick={() => setIsModalOpen(false)}><X size={20} /></button>
            </div>
            <form onSubmit={handleAddPatient} className="modal-body">
              <div className="form-group">
                <label>Patient Name</label>
                <input required type="text" value={formData.patient_name} onChange={e => setFormData({...formData, patient_name: e.target.value})} />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Blood Type</label>
                  <select value={formData.blood_type} onChange={e => setFormData({...formData, blood_type: e.target.value})}>
                    <option>O+</option><option>O-</option><option>A+</option><option>A-</option>
                    <option>B+</option><option>B-</option><option>AB+</option><option>AB-</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Urgency</label>
                  <select value={formData.urgency} onChange={e => setFormData({...formData, urgency: e.target.value})}>
                    <option>Critical</option>
                    <option>Urgent</option>
                    <option>Scheduled</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Hospital Name</label>
                <input required type="text" value={formData.hospital} onChange={e => setFormData({...formData, hospital: e.target.value})} />
              </div>
              <div className="form-group">
                <label>City</label>
                <input required type="text" value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Save & Auto-Route to AI</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
