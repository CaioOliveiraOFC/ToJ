(function(){
const D = JSON.parse(document.getElementById('dados').textContent);
const P = Object.fromEntries(D.participantes.map(p => [p.id, p]));
const J = Object.fromEntries(D.partidas.map(j => [j.chave, j]));
const PERF = Object.fromEntries(D.perfis);
const COR = {conservador:'var(--c-con)', moderado:'var(--c-mod)', hardcore:'var(--c-hard)'};
const FASE = Object.fromEntries(D.fases.map(f => [f[0], f[2]]));
const DESF = {executed:'executada', cancelled_control:'cancelada por controle', cancelled_death:'cancelada por morte', not_reached:'não alcançada'};
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const dot = c => `<span class="dot" style="background:${COR[c]}"></span>`;
const nome = id => `${dot(P[id].perfil)}${esc(P[id].nome)} <span class="muted">${id}</span>`;
const f2 = v => Number(v).toFixed(2);

try { const t = localStorage.getItem('copa03-tema'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
document.getElementById('tema').addEventListener('click', () => {
  const escuro = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === 'dark'
    : matchMedia('(prefers-color-scheme: dark)').matches;
  const novo = escuro ? 'light' : 'dark';
  document.documentElement.dataset.theme = novo;
  try { localStorage.setItem('copa03-tema', novo); } catch (e) {}
});

function abrir(aba){
  document.querySelectorAll('nav [role=tab]').forEach(b => b.setAttribute('aria-selected', b.dataset.aba === aba));
  document.querySelectorAll('main section').forEach(s => s.classList.toggle('ativa', s.id === aba));
  try { sessionStorage.setItem('copa03-aba', aba); } catch (e) {}
}
document.querySelectorAll('nav [role=tab]').forEach(b => b.addEventListener('click', () => abrir(b.dataset.aba)));
try { const a = sessionStorage.getItem('copa03-aba'); if (a && document.getElementById(a)) abrir(a); } catch (e) {}

const dica = document.getElementById('dica');
document.addEventListener('mouseover', e => {
  const alvo = e.target.closest('[data-tip]');
  if (!alvo) { dica.style.display = 'none'; return; }
  dica.textContent = alvo.getAttribute('data-tip'); dica.style.display = 'block';
});
document.addEventListener('mousemove', e => {
  if (dica.style.display === 'block') {
    const x = Math.min(e.clientX + 14, innerWidth - dica.offsetWidth - 8);
    dica.style.left = x + 'px'; dica.style.top = (e.clientY + 14) + 'px';
  }
});

function tabelaRodadas(j){
  const n1 = esc(P[j.p1].nome), n2 = esc(P[j.p2].nome);
  let h = `<table><thead><tr><th class=n>R</th><th>Ordem</th><th>${n1} (p1)</th><th>${n2} (p2)</th><th class=n>HP p1/p2</th><th class=n>MP p1/p2</th></tr></thead><tbody>`;
  for (const r of j.rodadas_detalhe) {
    const c = l => { const a = r.acoes[l]; return `${esc(a.acao)} — ${DESF[a.desfecho]}${a.desfecho==='executed' ? `, dano ${a.dano}${a.mp ? `, MP −${a.mp}` : ''}` : ''}`; };
    h += `<tr><td class=n>${r.n}</td><td>${r.ordem[0]} → ${r.ordem[1]} <span class=muted>(${r.criterio})</span></td><td>${c('p1')}</td><td>${c('p2')}</td><td class=n>${r.hp.p1} / ${r.hp.p2}</td><td class=n>${r.mp.p1} / ${r.mp.p2}</td></tr>`;
  }
  return h + '</tbody></table>';
}
function totais(j){
  const L = j.lados, linha = (r, f) => `<tr><td>${r}</td><td class=n>${f(L.p1)}</td><td class=n>${f(L.p2)}</td></tr>`;
  return `<table><thead><tr><th>Total</th><th class=n>${esc(P[j.p1].nome)}</th><th class=n>${esc(P[j.p2].nome)}</th></tr></thead><tbody>`
   + linha('Dano (golpes + DoT)', e => `${e.dano} (${e.dano_golpes} + ${e.dano_dot})`)
   + linha('Cura (skill + roubo)', e => `${e.cura} (${e.cura_skill} + ${e.roubo_de_vida})`)
   + linha('MP gasto', e => e.mp) + linha('Skills / básicos', e => `${e.skills} / ${e.basicos}`)
   + linha('Acertos / erros', e => `${e.acertos} / ${e.erros}`) + linha('Críticos (dano)', e => `${e.criticos} (${e.dano_critico})`)
   + linha('Agiu primeiro', e => e.primeiro) + linha('Ações perdidas por controle', e => e.perdidas_controle)
   + linha('Égide absorveu', e => e.egide) + '</tbody></table>';
}
function detalhe(chave){
  const j = J[chave]; if (!j) return;
  const v = P[j.vencedor];
  const status = l => (j.lados[l].status_aplicados.join(', ') || '—');
  document.getElementById('detalhe-corpo').innerHTML = `
   <h2>${esc(j.titulo)}</h2>
   <p class="sec">Seed <code>${j.seed}</code> · ${j.rodadas} rodadas · ${j.sorteios} sorteios · fidelidade ${j.fidelidade ? 'idêntica' : 'DIVERGENTE'}${j.zebra ? ' · <span class="tag z">zebra</span>' : ''}</p>
   <table><tbody>${['p1','p2'].map(l => { const p = P[j[l]]; return `<tr><td>${l}</td><td>${nome(p.id)}</td><td>${esc(PERF[p.perfil])}/${esc(p.politica)} · andar ${p.andar} · nv ${p.nivel}</td><td class=n>OP ${f2(p.op)}</td></tr><tr><td></td><td colspan=3 class="muted">${esc(p.foco)} — ${esc(p.deck.join(', '))}</td></tr>`; }).join('')}</tbody></table>
   <p><b>Vencedor:</b> ${nome(v.id)} por <code>${j.motivo}</code>, com ${j.hp_vencedor}/${j.hp_max_vencedor} de HP. ΔOP ${j.delta_op >= 0 ? '+' : ''}${f2(j.delta_op)}.</p>
   <h3>Totais</h3>${totais(j)}
   <p class="sec">Status aplicados — ${esc(P[j.p1].nome)}: ${esc(status('p1'))}; ${esc(P[j.p2].nome)}: ${esc(status('p2'))}.</p>
   <h3>Rodada a rodada</h3><div class="rolagem">${tabelaRodadas(j)}</div>`;
  document.getElementById('detalhe').classList.add('aberto');
  document.querySelectorAll('.jogo').forEach(g => g.classList.toggle('sel', g.dataset.jogo === chave));
}
document.getElementById('fechar').addEventListener('click', () => document.getElementById('detalhe').classList.remove('aberto'));
document.addEventListener('keydown', e => { if (e.key === 'Escape') document.getElementById('detalhe').classList.remove('aberto'); });
document.addEventListener('click', e => { const g = e.target.closest('[data-jogo]'); if (g) detalhe(g.dataset.jogo); });
document.addEventListener('keydown', e => { if (e.key === 'Enter') { const g = e.target.closest && e.target.closest('[data-jogo]'); if (g) detalhe(g.dataset.jogo); } });

function confrontos(){
  const fase = document.getElementById('f-fase').value, cl = document.getElementById('f-perfil').value;
  const z = document.getElementById('f-zebra').checked, q = document.getElementById('f-busca').value.toLowerCase();
  const corpo = document.querySelector('#t-confrontos tbody');
  corpo.innerHTML = D.partidas.filter(j => (!fase || j.fase === fase) && (!z || j.zebra)
    && (!cl || P[j.p1].perfil === cl || P[j.p2].perfil === cl)
    && (!q || P[j.p1].nome.toLowerCase().includes(q) || P[j.p2].nome.toLowerCase().includes(q)))
   .map(j => `<tr class="clicavel" data-jogo="${j.chave}"><td>${esc(j.nome_fase)} ${j.fase === 'final' ? '' : j.indice}</td><td>${nome(j.p1)}</td><td class=n>${f2(j.op.p1)}</td><td>${nome(j.p2)}</td><td class=n>${f2(j.op.p2)}</td><td>${esc(P[j.vencedor].nome)}${j.zebra ? ' <span class="tag z">zebra</span>' : ''}</td><td class=n>${j.rodadas}</td><td class=n>${j.hp_vencedor}/${j.hp_max_vencedor}</td><td class=n>${j.delta_op >= 0 ? '+' : ''}${f2(j.delta_op)}</td></tr>`).join('');
}
['f-fase','f-perfil','f-zebra','f-busca'].forEach(id => document.getElementById(id).addEventListener('input', confrontos));
confrontos();

let ordem = {k:'op', d:-1};
function participantes(){
  const cl = document.getElementById('p-perfil').value, po = document.getElementById('p-politica').value, q = document.getElementById('p-busca').value.toLowerCase();
  const lista = D.participantes.filter(p => (!cl || p.perfil === cl) && (!po || p.politica === po)
    && (!q || (p.nome + ' ' + p.id + ' ' + p.foco + ' ' + p.deck.join(' ')).toLowerCase().includes(q)));
  lista.sort((a, b) => (a[ordem.k] > b[ordem.k] ? 1 : a[ordem.k] < b[ordem.k] ? -1 : 0) * ordem.d);
  document.querySelector('#t-participantes tbody').innerHTML = lista.map(p => `<tr><td>${p.id}</td><td>${dot(p.perfil)}${esc(p.nome)}</td><td>${esc(PERF[p.perfil])}/${esc(p.politica)}</td><td class=n>${p.andar}</td><td class=n>${p.nivel}</td><td class=n>${f2(p.op)}</td><td class=n>${p.hp}</td><td class=n>${p.mp}</td><td class=n>${p.st}</td><td class=n>${p.ag}</td><td class=n>${p.df}</td><td><b>${esc(p.foco)}</b><br><span class="muted">${esc(p.deck.join(', '))}</span></td><td class=n>${p.vitorias}</td><td>${p.campeao ? 'Campeão' : esc(FASE[p.fase]) + (p.eliminado_por ? ' · por ' + esc(P[p.eliminado_por].nome) : '')}</td></tr>`).join('');
}
document.querySelectorAll('#t-participantes th.ord').forEach(th => th.addEventListener('click', () => { const k = th.dataset.k; ordem = {k, d: ordem.k === k ? -ordem.d : (['nome','id','perfil'].includes(k) ? 1 : -1)}; participantes(); }));
['p-perfil','p-politica','p-busca'].forEach(id => document.getElementById(id).addEventListener('input', participantes));
participantes();

const camp = D.campeao;
if (camp) {
  const jogos = D.partidas.filter(j => j.p1 === camp || j.p2 === camp);
  document.getElementById('trajetoria').innerHTML = `<p>${nome(camp)} · Guerreiro ${esc(PERF[P[camp].perfil])}/${esc(P[camp].politica)}, extraído no andar ${P[camp].andar}, nível ${P[camp].nivel} · OP ${f2(P[camp].op)} · <i>${esc(P[camp].foco)}</i></p><table><thead><tr><th>Fase</th><th>Adversário</th><th class=n>OP</th><th class=n>Rodadas</th><th class=n>HP final</th></tr></thead><tbody>`
   + jogos.map(j => { const o = j.p1 === camp ? j.p2 : j.p1; return `<tr class="clicavel" data-jogo="${j.chave}"><td>${esc(j.nome_fase)}</td><td>${nome(o)}</td><td class=n>${f2(P[o].op)}</td><td class=n>${j.rodadas}</td><td class=n>${j.hp_vencedor}/${j.hp_max_vencedor}</td></tr>`; }).join('') + '</tbody></table>';
}
const zb = D.agregados.zebras;
document.getElementById('zebras').innerHTML = zb.length ? `<table><thead><tr><th>Partida</th><th>Vencedor</th><th class=n>OP</th><th>Perdedor</th><th class=n>OP</th><th class=n>ΔOP</th></tr></thead><tbody>` + zb.map(r => `<tr class="clicavel" data-jogo="${r.chave}"><td>${esc(r.nome_fase)}</td><td>${nome(r.vencedor)}</td><td class=n>${f2(P[r.vencedor].op)}</td><td>${nome(r.perdedor)}</td><td class=n>${f2(P[r.perdedor].op)}</td><td class=n>${f2(r.delta_op)}</td></tr>`).join('') + '</tbody></table>' : '<p>Nenhuma.</p>';

if (D.final) {
  const F = D.final, stats = ['hp','mp','st','mg','ag','df'];
  let h = '<table><thead><tr><th>Rodada</th><th>Lado</th>' + stats.map(s => `<th class=n>${s} (valor / REF / √)</th>`).join('') + '<th class=n>build</th><th class=n>mod. nível</th><th class=n>score</th></tr></thead><tbody>';
  for (const [n, leit] of F.iniciativa) for (const l of ['p1','p2']) {
    const x = leit[l];
    h += `<tr><td>R${n}</td><td>${esc(P[F.ids[l]].nome)}</td>` + stats.map(s => `<td class=n>${x.parcelas[s][0]} / ${Number(x.parcelas[s][1]).toFixed(3)} / ${Number(x.parcelas[s][2]).toFixed(6)}</td>`).join('') + `<td class=n>${Number(x.build).toFixed(9)}</td><td class=n>${x.modificador}</td><td class=n>${Number(x.score).toFixed(9)}</td></tr>`;
  }
  document.getElementById('tabela-iniciativa').innerHTML = h + '</tbody></table>';
  const j = J[F.chave];
  document.getElementById('final-partida').innerHTML = `<h3>A final rodada a rodada</h3><div class="rolagem">${tabelaRodadas(j)}</div><h3>Totais</h3>${totais(j)}`;
}
})();
