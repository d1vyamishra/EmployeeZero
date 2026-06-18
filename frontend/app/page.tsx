'use client';

import React, { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

interface Lead {
  id: string | number;
  full_name: string;
  company_name: string;
  status: string;
  created_at: string;
  email: string;
}

interface ReplyLog {
  id: string | number;
  incoming_message: string;
  ai_reply_draft: string;
  status: string;
  created_at: string;
}

export default function CompleteGlassDashboard() {
  const [currentTab, setCurrentTab] = useState<'overview' | 'leads'>('overview');
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [replyLogs, setReplyLogs] = useState<ReplyLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchInitialData() {
      try {
        const { data, error } = await supabase
          .from('leads')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;
        if (data) {
          setLeads(data);
          if (data.length > 0) setSelectedLead(data[0]);
        }
      } catch (err) {
        console.error('Database connection error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchInitialData();
  }, []);

  useEffect(() => {
    async function fetchThreadLogs() {
      if (!selectedLead) return;
      try {
        const { data, error } = await supabase
          .from('lead_replies')
          .select('*')
          .order('created_at', { ascending: true });

        if (error) throw error;
        if (data) setReplyLogs(data);
      } catch (err) {
        console.error('Error compiling message streams:', err);
      }
    }
    fetchThreadLogs();
  }, [selectedLead]);


  const totalLeadsCount = leads.length;
  const repliedLeadsCount = leads.filter(l => l.status === 'Replied').length;
  const emailedLeadsCount = leads.filter(l => l.status === 'Emailed').length;
  const conversionRate = totalLeadsCount > 0 ? ((repliedLeadsCount / totalLeadsCount) * 100).toFixed(1) : '0.0';

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans relative overflow-hidden">
      
 
      <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-[160px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[700px] h-[700px] bg-emerald-500/15 rounded-full blur-[180px] pointer-events-none z-0" />


      <aside className="w-64 bg-slate-900/40 backdrop-blur-xl border-r border-white/10 p-6 flex flex-col justify-between z-10">
        <div>
          <div className="flex items-center space-x-3 mb-10">
            <div className="w-9 h-9 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center font-bold tracking-wider shadow-lg shadow-indigo-500/20">
              0
            </div>
            <span className="font-bold text-lg tracking-tight text-white">Employee Zero</span>
          </div>
          
          <nav className="space-y-2">
            <button 
              onClick={() => setCurrentTab('overview')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl border transition-all duration-200 text-left ${
                currentTab === 'overview' 
                  ? 'bg-white/10 text-indigo-400 font-medium border-white/10 shadow-md' 
                  : 'text-slate-400 border-transparent hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              <span>📊 System Overview</span>
            </button>
            <button 
              onClick={() => setCurrentTab('leads')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl border transition-all duration-200 text-left ${
                currentTab === 'leads' 
                  ? 'bg-white/10 text-indigo-400 font-medium border-white/10 shadow-md' 
                  : 'text-slate-400 border-transparent hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              <span>👥 Conversation Logs</span>
            </button>
          </nav>
        </div>
        
        <div className="border-t border-white/10 pt-4 text-[11px] text-slate-500 tracking-wide">
          FOUNDER: <span className="text-slate-400 font-medium">Divya Prakash Mishra</span>
        </div>
      </aside>


      {loading ? (
        <div className="flex-1 flex items-center justify-center z-10">
          <p className="text-sm font-medium tracking-wide text-indigo-400 animate-pulse">Syncing with Supabase Cluster...</p>
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden z-10">
          

          {currentTab === 'overview' && (
            <section className="flex-1 p-8 overflow-y-auto space-y-8">
              <div>
                <h1 className="text-3xl font-extrabold text-white tracking-tight">Command Center</h1>
                <p className="text-sm text-slate-400 mt-1">Real-time optimization matrix running via background loops.</p>
              </div>


              <div className="grid grid-cols-1 md-grid-cols-4 gap-5">
                <div className="bg-white/5 backdrop-blur-md border border-white/10 p-5 rounded-2xl shadow-xl">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Total Tracked Leads</span>
                  <span className="text-3xl font-black text-white block mt-2">{totalLeadsCount}</span>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 p-5 rounded-2xl shadow-xl">
                  <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block">Autonomous Pitches</span>
                  <span className="text-3xl font-black text-white block mt-2">{emailedLeadsCount + repliedLeadsCount}</span>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 p-5 rounded-2xl shadow-xl">
                  <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block">Active Replies</span>
                  <span className="text-3xl font-black text-emerald-400 block mt-2">{repliedLeadsCount}</span>
                </div>
                <div className="bg-white/5 backdrop-blur-md border border-white/10 p-5 rounded-2xl shadow-xl">
                  <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider block">Conversion Yield</span>
                  <span className="text-3xl font-black text-white block mt-2">{conversionRate}%</span>
                </div>
              </div>

              <div className="bg-white/[0.02] backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                <h2 className="text-lg font-bold text-white mb-4">Lead Status Matrix</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-white/10 text-xs font-semibold uppercase tracking-wider text-slate-400">
                        <th className="pb-3 pt-2">Full Name</th>
                        <th className="pb-3 pt-2">Company Target</th>
                        <th className="pb-3 pt-2">Email Address</th>
                        <th className="pb-3 pt-2">Current Flag</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-sm text-slate-300">
                      {leads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-white/[0.02] transition-colors">
                          <td className="py-3.5 font-medium text-white">{lead.full_name || 'Anonymous Row'}</td>
                          <td className="py-3.5">{lead.company_name || 'Not Flagged'}</td>
                          <td className="py-3.5 font-mono text-xs text-slate-400">{lead.email}</td>
                          <td className="py-3.5">
                            <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-medium tracking-wide ${
                              lead.status === 'Replied' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                              lead.status === 'Emailed' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' :
                              'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            }`}>
                              {lead.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>
          )}

         
          {currentTab === 'leads' && (
            <div className="flex-1 flex overflow-hidden">
            
              <section className="w-96 bg-slate-900/20 backdrop-blur-md border-r border-white/10 flex flex-col">
                <div className="p-6 border-b border-white/10">
                  <h1 className="text-xl font-bold text-white">Active Pipelines</h1>
                  <p className="text-xs text-slate-400 mt-1">Select targets to inspect conversation threads</p>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {leads.map((lead) => (
                    <div 
                      key={lead.id} 
                      onClick={() => setSelectedLead(lead)}
                      className={`p-4 border rounded-2xl transition-all duration-300 cursor-pointer shadow-lg backdrop-blur-xl group ${
                        selectedLead?.id === lead.id 
                          ? 'bg-white/10 border-indigo-500/50 shadow-indigo-500/5' 
                          : 'bg-white/5 border-white/5 hover:border-white/20'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <h3 className="font-medium text-sm text-white group-hover:text-indigo-400 transition-colors">
                          {lead.full_name || 'Unnamed Lead'}
                        </h3>
                      </div>
                      <p className="text-xs text-slate-400 mb-3">{lead.company_name || 'No Company'}</p>
                      <div className="flex justify-between items-center">
                        <p className="text-[11px] text-slate-500 truncate w-40 font-mono">{lead.email}</p>
                        <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-medium tracking-wide ${
                          lead.status === 'Replied' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                          lead.status === 'Emailed' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' :
                          'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}>
                          {lead.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="flex-1 flex flex-col overflow-y-auto p-8 bg-slate-950/40 backdrop-blur-sm">
                <div className="max-w-3xl w-full mx-auto space-y-6">
                  {selectedLead ? (
                    <>
                      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 flex justify-between items-center shadow-2xl relative overflow-hidden">
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Thread Status Analyzer</span>
                          <h2 className="text-2xl font-bold text-white tracking-tight mt-0.5">{selectedLead.full_name}</h2>
                          <p className="text-xs text-slate-400">{selectedLead.company_name}</p>
                        </div>
                        <div className="text-right">
                          <span className="text-sm font-semibold text-emerald-400 block bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/30">
                            ⚡ 60% BPO Workload Cut
                          </span>
                        </div>
                      </div>

                      <div className="space-y-4">
                        {replyLogs.length === 0 ? (
                          <div className="p-8 border border-dashed border-white/10 rounded-2xl text-center text-slate-500 text-sm">
                            No active back-and-forth conversation logged for this row yet. Outbound flow active.
                          </div>
                        ) : (
                          replyLogs.map((log) => (
                            <React.Fragment key={log.id}>
                              <div className="bg-white/5 backdrop-blur-md border border-white/10 p-6 rounded-2xl max-w-xl shadow-xl">
                                <div className="flex items-center space-x-2 mb-3 text-xs font-medium text-slate-400">
                                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                                  <span>Incoming Lead Inquiry</span>
                                </div>
                                <p className="text-sm text-slate-300 leading-relaxed font-normal">
                                  "{log.incoming_message}"
                                </p>
                              </div>

                              <div className="bg-indigo-950/30 backdrop-blur-xl border border-indigo-500/40 p-6 rounded-2xl max-w-xl ml-auto shadow-2xl">
                                <div className="flex items-center justify-between mb-3 text-xs font-medium text-indigo-400">
                                  <div className="flex items-center space-x-2">
                                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                                    <span>Employee Zero Auto-Responder</span>
                                  </div>
                                  <span className="text-[10px] text-indigo-400/60 font-mono">Gmail SMTP Secure</span>
                                </div>
                                <p className="text-sm text-slate-300 leading-relaxed font-normal whitespace-pre-line">
                                  {log.ai_reply_draft}
                                </p>
                              </div>
                            </React.Fragment>
                          ))
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="text-center p-20 text-slate-500 text-sm">
                      Select a lead row from the active panels to view historical logs.
                    </div>
                  )}
                </div>
              </section>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
