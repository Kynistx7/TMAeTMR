const META_TMA = 1.32;
const META_TMR = 6.00;

let user_id = localStorage.getItem('user_id');
let user_nome = localStorage.getItem('user_nome');

console.log('Dados do usuário:', { user_id, user_nome });

// Redireciona se não logado
if (!user_id && (window.location.pathname.includes("tempos") || window.location.pathname.includes("index.html"))) {
  console.log('Usuário não logado, redirecionando...');
  window.location.href = "/login";
}

const tabela = document.getElementById('tabela');
const form = document.getElementById('form');
const limparBtn = document.getElementById('limpar-registros');

// Utilidades de tempo
function timeToHMS(timeStr) {
  const parts = timeStr.split(':');
  const h = parseInt(parts[0]) || 0;
  const m = parseInt(parts[1]) || 0;
  const s = parseInt(parts[2]) || 0;
  return { h, m, s };
}

function hmsToSeconds(h, m, s = 0) {
  return h * 3600 + m * 60 + s;
}

function somarTemposHMS(tv, tr) {
  let totalSeconds = hmsToSeconds(tv.h, tv.m, tv.s) + hmsToSeconds(tr.h, tr.m, tr.s);
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return { h, m, s };
}

function secondsToMinutes(seconds) {
  return seconds / 60;
}

async function carregarRegistros() {
  if (!user_id) {
    console.log('Sem user_id, não carregando registros');
    return;
  }
  
  console.log(`Carregando registros para user_id: ${user_id}`);
  
  try {
    const res = await fetch(`/api/registros/${user_id}`);
    console.log('Resposta do servidor:', res.status);
    
    if (!res.ok) {
      throw new Error(`Erro HTTP: ${res.status}`);
    }
    
    const registros = await res.json();
    console.log('Registros recebidos:', registros);
    
    tabela.innerHTML = "";
    
    if (registros.length === 0) {
      tabela.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #666;">Nenhum registro encontrado</td></tr>';
      return;
    }
    
    registros.forEach(op => {
      const tmaStatus = op.tma <= META_TMA ? "✅ Dentro da meta" : "⚠️ Fora da meta";
      const tmrStatus = op.tmr <= META_TMR ? "✅ Dentro da meta" : "⚠️ Fora da meta";
      
      // Formatear data para exibição (DD/MM/YYYY)
      const dataFormatada = op.data_registro ? 
        new Date(op.data_registro + 'T00:00:00').toLocaleDateString('pt-BR') : 
        'N/A';
      
      const linha = document.createElement('tr');
      linha.innerHTML = `
        <td>${op.nome_operador}</td>
        <td>${dataFormatada}</td>
        <td>${op.numero_pdv || 'N/A'}</td>
        <td>
          <strong>${op.tma} min/cupom</strong><br>
          <small style="color: ${op.tma <= META_TMA ? 'green' : 'red'}">${tmaStatus}</small>
        </td>
        <td>
          <strong>${op.tmr} seg/item</strong><br>
          <small style="color: ${op.tmr <= META_TMR ? 'green' : 'red'}">${tmrStatus}</small>
        </td>
        <td>
          ${op.tma <= META_TMA && op.tmr <= META_TMR ? 
            "<span style='color: green'>✅ Todas as metas atingidas</span>" : 
            (op.tma > META_TMA && op.tmr > META_TMR ? 
              "<span style='color: red'>⚠️ Ambas fora da meta</span>" :
              (op.tma > META_TMA ? 
                "<span style='color: orange'>TMA fora da meta</span>" : 
                "<span style='color: orange'>TMR fora da meta</span>"))}
        </td>
      `;
      linha.className = (op.tma <= META_TMA && op.tmr <= META_TMR) ? "meta-ok" : "meta-fail";
      tabela.appendChild(linha);
    });
  } catch (error) {
    console.error('Erro ao carregar registros:', error);
    tabela.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Erro ao carregar registros</td></tr>';
  }
}

if (form) {
  form.addEventListener('submit', async e => {
    e.preventDefault();
    console.log('Formulário enviado');
    
    const nome = document.getElementById('nome').value.trim();
    const data_registro = document.getElementById('data_registro').value;
    const numero_pdv = document.getElementById('numero_pdv').value.trim();
    const tvStr = document.getElementById('tv').value;
    const trStr = document.getElementById('tr').value;
    const cupons = parseInt(document.getElementById('cupons').value);
    const itens = parseInt(document.getElementById('itens').value);

    console.log('Dados do formulário:', { nome, data_registro, numero_pdv, tvStr, trStr, cupons, itens, user_id });

    // Validações básicas
    if (!nome || !data_registro || !numero_pdv || !tvStr || !trStr || !cupons || !itens) {
      alert('Por favor, preencha todos os campos!');
      return;
    }

    if (cupons <= 0 || itens <= 0) {
      alert('Quantidade de cupons e itens deve ser maior que zero!');
      return;
    }

    if (!user_id) {
      alert('Usuário não identificado. Faça login novamente.');
      window.location.href = '/login';
      return;
    }

    // Converter tempos para HMS
    const tv = timeToHMS(tvStr);
    const tr = timeToHMS(trStr);
    
    // Somar TV + TR (tempo total gasto)
    const tempoTotal = somarTemposHMS(tv, tr);
    const tempoTotalSegundos = hmsToSeconds(tempoTotal.h, tempoTotal.m, tempoTotal.s);
    
    // Cálculo TMA: Tempo total (em minutos) / quantidade de cupons
    let tma = secondsToMinutes(tempoTotalSegundos) / cupons;
    tma = parseFloat(tma.toFixed(2));

    // Cálculo TMR: Tempo de venda (TV em segundos) / quantidade de itens
    const tvSegundos = hmsToSeconds(tv.h, tv.m, tv.s);
    let tmr = tvSegundos / itens;
    tmr = parseFloat(tmr.toFixed(2));

    console.log(`Cálculos: TV=${tvStr}, TR=${trStr}, Cupons=${cupons}, Itens=${itens}`);
    console.log(`TMA = ${secondsToMinutes(tempoTotalSegundos).toFixed(2)} min / ${cupons} cupons = ${tma} min/cupom`);
    console.log(`TMR = ${tvSegundos} seg / ${itens} itens = ${tmr} seg/item`);

    const dadosParaEnvio = { 
      nome_operador: nome,
      data_registro: data_registro,
      numero_pdv: numero_pdv,
      tma, 
      tmr, 
      user_id: parseInt(user_id) 
    };
    
    console.log('Enviando dados:', dadosParaEnvio);

    try {
      // Enviar para o servidor
      const response = await fetch("/api/registros", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(dadosParaEnvio)
      });

      console.log('Resposta do servidor:', response.status);

      if (response.ok) {
        const resultado = await response.json();
        console.log('Sucesso:', resultado);
        form.reset();
        await carregarRegistros(); // Aguarda carregar antes de mostrar o alert
        alert('Registro salvo com sucesso!');
      } else {
        const error = await response.json();
        console.error('Erro do servidor:', error);
        alert(`Erro ao salvar: ${error.erro || 'Erro desconhecido'}`);
      }
    } catch (error) {
      console.error('Erro na requisição:', error);
      alert('Erro de conexão com o servidor');
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  if (tabela) carregarRegistros();
  if (user_nome && document.getElementById('usuario-logado')) {
    document.getElementById('usuario-logado').innerText = user_nome;
  }
  
  // Definir data atual por padrão
  const dataInput = document.getElementById('data_registro');
  if (dataInput) {
    const hoje = new Date();
    const dataFormatada = hoje.toISOString().split('T')[0]; // YYYY-MM-DD
    dataInput.value = dataFormatada;
  }
});

// Limpar registros do usuário
if (limparBtn) {
  limparBtn.addEventListener('click', async () => {
    if (confirm("Tem certeza que deseja limpar todos os registros?")) {
      await fetch(`/api/registros/clear/${user_id}`, { method: "DELETE" });
      carregarRegistros();
    }
  });
}

// Logout
const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
  logoutBtn.onclick = async () => {
    await fetch("/api/logout", {method: "POST"});
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_nome');
    window.location.href = "/login";
  };
}

// Botão de teste
const testeBtn = document.getElementById('teste-usuario');
if (testeBtn) {
  testeBtn.addEventListener('click', async () => {
    console.log('=== TESTE COMPLETO DO USUÁRIO ===');
    console.log('user_id:', user_id);
    console.log('user_nome:', user_nome);
    console.log('localStorage user_id:', localStorage.getItem('user_id'));
    console.log('localStorage user_nome:', localStorage.getItem('user_nome'));
    
    // Testar se consegue acessar a API de registros
    if (user_id) {
      try {
        console.log(`Testando API: /api/registros/${user_id}`);
        const response = await fetch(`/api/registros/${user_id}`);
        const data = await response.json();
        console.log('Resposta da API:', data);
        
        alert(`Usuário: ${user_nome || 'Não definido'}\nID: ${user_id || 'Não definido'}\nRegistros encontrados: ${data.length || 0}`);
      } catch (error) {
        console.error('Erro ao testar API:', error);
        alert(`Usuário: ${user_nome || 'Não definido'}\nID: ${user_id || 'Não definido'}\nErro ao acessar API: ${error.message}`);
      }
    } else {
      alert('❌ Usuário não está logado!');
    }
  });
}

// Botão para recarregar dados
const recarregarBtn = document.getElementById('recarregar-dados');
if (recarregarBtn) {
  recarregarBtn.addEventListener('click', async () => {
    console.log('🔄 Forçando recarregamento dos dados...');
    await carregarRegistros();
    alert('Dados recarregados!');
  });
}