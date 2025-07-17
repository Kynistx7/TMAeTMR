const META_TMA = 1.32;
const META_TMR = 6.00;

let user_id = localStorage.getItem('user_id');
let user_nome = localStorage.getItem('user_nome');
let is_admin = localStorage.getItem('is_admin') === 'true';

console.log('Dados do usuário:', { user_id, user_nome, is_admin });

// Redireciona se não logado
if (!user_id && (window.location.pathname.includes("tempos") || window.location.pathname.includes("index.html"))) {
  console.log('Usuário não logado, redirecionando...');
  window.location.href = "/login";
}

const tabela = document.getElementById('tabela');
const form = document.getElementById('form');
const limparBtn = document.getElementById('limpar-registros');

// Variáveis globais
let ultimosPontosGraficoTMA = [];
let ultimosPontosGraficoTMR = [];
let operadoresProblematicos = [];
let registrosAdmin = []; // Armazenar registros para uso nas funções de pesquisa

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
        op.data_registro.split('-').reverse().join('/') : 
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

document.addEventListener('DOMContentLoaded', async () => {
  console.log('DOM carregado, inicializando aplicação...');
  console.log('Página atual:', window.location.pathname);
  console.log('Status de admin:', is_admin);
  
  if (tabela) {
    console.log('Tabela encontrada, carregando registros...');
    carregarRegistros();
  }
  
  if (user_nome && document.getElementById('usuario-logado')) {
    console.log('Atualizando nome de usuário na interface...');
    document.getElementById('usuario-logado').innerText = user_nome;
  }
  
  // Verificar se usuário é admin consultando a API
  console.log('Verificando status de admin...');
  await verificarStatusAdmin();
  console.log('Status de admin após verificação:', is_admin);
  
  // Se estiver na página de admin, carregar dados administrativos
  if (window.location.pathname.includes('admin')) {
    console.log('Estamos na página de admin, preparando para carregar dados administrativos...');
    
    // Verificar se o elemento do painel existe
    const painelAlerta = document.getElementById('painel-operadores-alerta');
    if (!painelAlerta) {
      console.error('ERRO: Elemento painel-operadores-alerta não encontrado!');
      console.log('IDs disponíveis na página:', 
        Array.from(document.querySelectorAll('[id]')).map(el => el.id));
    } else {
      console.log('Elemento painel-operadores-alerta encontrado:', painelAlerta);
    }
    
    if (is_admin) {
      console.log('Usuário é admin, carregando dados administrativos...');
      
      // Dar um pequeno delay para garantir que a página carregou completamente
      setTimeout(() => {
        carregarRegistrosAdmin();
        
        // Configurar event listener para o campo de pesquisa de operadores
        const campoPesquisa = document.getElementById('pesquisa-nome-operador');
        if (campoPesquisa) {
          console.log('Campo de pesquisa de operadores encontrado, configurando eventos');
          
          // Event listener para pesquisa em tempo real (com debounce)
          let timeoutId;
          campoPesquisa.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
              const termoPesquisa = this.value.trim();
              console.log('Pesquisando operadores por:', termoPesquisa);
              filtrarOperadoresPorNome(termoPesquisa);
            }, 300); // 300ms de debounce
          });
          
          // Event listener para tecla Enter
          campoPesquisa.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
              event.preventDefault();
              const termoPesquisa = this.value.trim();
              console.log('Pesquisa por Enter:', termoPesquisa);
              filtrarOperadoresPorNome(termoPesquisa);
            }
          });
        } else {
          console.error('Campo de pesquisa de operadores não encontrado');
        }
      }, 500);
    } else {
      console.log('Usuário não é admin, não carregando dados administrativos');
    }
  }
  
  // Definir data atual por padrão
  const dataInput = document.getElementById('data_registro');
  if (dataInput) {
    const hoje = new Date();
    const dataFormatada = hoje.toISOString().split('T')[0]; // YYYY-MM-DD
    dataInput.value = dataFormatada;
  }
  
  // Configurar o filtro de criticidade, se existir
  const filtroCriticidade = document.getElementById('filtro-criticidade');
  if (filtroCriticidade) {
    console.log('Configurando filtro de criticidade...');
    filtroCriticidade.addEventListener('change', function() {
      const valor = this.value;
      console.log('Filtro alterado para:', valor);
      
      const cards = document.querySelectorAll('.card-operador-alerta');
      if (valor === 'todos') {
        cards.forEach(card => card.style.display = 'block');
      } else {
        cards.forEach(card => {
          if (card.classList.contains(valor + '-criticidade')) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        });
      }
    });
  }
  
  // Configurar o campo de pesquisa por nome de operador
  const pesquisaNomeOperador = document.getElementById('pesquisa-nome-operador');
  if (pesquisaNomeOperador) {
    console.log('Configurando campo de pesquisa por nome de operador...');
    
    // Pesquisar ao pressionar Enter
    pesquisaNomeOperador.addEventListener('keyup', function(event) {
      if (event.key === 'Enter') {
        const termo = this.value.trim();
        console.log('Pesquisando operador:', termo);
        filtrarOperadoresPorNome(termo);
      }
    });
    
    // Limpar a pesquisa quando o campo ficar vazio
    pesquisaNomeOperador.addEventListener('input', function() {
      if (this.value.trim() === '') {
        console.log('Campo de pesquisa vazio, mostrando todos os operadores');
        filtrarOperadoresPorNome('');
      }
    });
  }
});

// Função para verificar se usuário é admin
async function verificarStatusAdmin() {
  if (!user_id) return;
  
  try {
    const response = await fetch('/api/admin/stats');
    if (response.status === 200) {
      // Se conseguiu acessar a rota admin, é admin
      const adminBtn = document.getElementById('admin-btn');
      if (adminBtn) {
        adminBtn.style.display = 'inline-block';
      }
      localStorage.setItem('is_admin', 'true');
      console.log('Usuário é administrador');
    } else if (response.status === 403) {
      // Não é admin
      localStorage.setItem('is_admin', 'false');
      console.log('Usuário não é administrador');
    }
  } catch (error) {
    console.log('Erro ao verificar status admin:', error);
    localStorage.setItem('is_admin', 'false');
  }
}

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

// Função para carregar todos os registros para o admin
async function carregarRegistrosAdmin() {
  if (!is_admin || !window.location.pathname.includes('admin')) {
    return;
  }
  
  const painelAlerta = document.getElementById('painel-operadores-alerta');
  if (!painelAlerta) {
    console.error('Elemento painel-operadores-alerta não encontrado');
    return;
  }
  
  painelAlerta.innerHTML = '<div class="carregando"><div class="loader"></div>Analisando dados dos operadores...</div>';
  
  try {
    const res = await fetch('/api/admin/registros');
    
    if (!res.ok) {
      throw new Error(`Erro HTTP: ${res.status}`);
    }
    
    const registros = await res.json();
    
    // Armazenar registros globalmente para uso nas funções de pesquisa
    console.log('Registros carregados:', registros.length);
    window.registrosAdmin = registros; // Garantir acesso global
    registrosAdmin = registros;
    
    if (registros.length === 0) {
      painelAlerta.innerHTML = '<div class="alerta-ok">Não há registros disponíveis para análise</div>';
      return [];
    }
    
    const operadoresProblematicos = analisarOperadoresProblematicos(registros);
    exibirOperadoresComProblemas(operadoresProblematicos);
    
    // Aplicar o filtro de pesquisa após carregar
    const termoPesquisa = document.getElementById('pesquisa-nome-operador')?.value || '';
    if (termoPesquisa) {
      filtrarOperadoresPorNome(termoPesquisa);
    }
    
    return registros;
  } catch (error) {
    console.error('Erro ao carregar registros administrativos:', error);
    
    if (painelAlerta) {
      painelAlerta.innerHTML = `<div class="erro-admin">Erro ao carregar dados administrativos: ${error.message}</div>`;
    }
    return [];
  }
}

// Função para analisar dados e identificar operadores que precisam de atenção
function analisarOperadoresProblematicos(registros) {
  // Agrupar registros por operador
  const registrosPorOperador = {};
  
  registros.forEach(reg => {
    if (!registrosPorOperador[reg.nome_operador]) {
      registrosPorOperador[reg.nome_operador] = [];
    }
    registrosPorOperador[reg.nome_operador].push(reg);
  });
  
  // Analisar cada operador
  const operadoresProblematicos = [];
  
  for (const nome in registrosPorOperador) {
    const registrosOperador = registrosPorOperador[nome];
    
    // Calcular médias de TMA e TMR
    const mediaTMA = registrosOperador.reduce((acc, reg) => acc + reg.tma, 0) / registrosOperador.length;
    const mediaTMR = registrosOperador.reduce((acc, reg) => acc + reg.tmr, 0) / registrosOperador.length;
    
    // Calcular percentual fora da meta
    const registrosForaMetaTMA = registrosOperador.filter(reg => reg.tma > META_TMA).length;
    const registrosForaMetaTMR = registrosOperador.filter(reg => reg.tmr > META_TMR).length;
    
    const percentualForaMetaTMA = (registrosForaMetaTMA / registrosOperador.length) * 100;
    const percentualForaMetaTMR = (registrosForaMetaTMR / registrosOperador.length) * 100;
    
    // Verificar tendências (últimos 3 registros)
    const ultimosRegistros = [...registrosOperador].sort((a, b) => 
      new Date(b.data_registro) - new Date(a.data_registro)
    ).slice(0, 3);
    
    const tempiora = ultimosRegistros.length >= 2 && 
                    ultimosRegistros[0].tma > ultimosRegistros[1].tma &&
                    ultimosRegistros[0].tmr > ultimosRegistros[1].tmr;
    
    // Pontuar o operador (quanto maior a pontuação, mais atenção é necessária)
    let pontuacao = 0;
    
    // Pontuação baseada na média
    pontuacao += mediaTMA > META_TMA ? 30 : 0;
    pontuacao += mediaTMR > META_TMR ? 30 : 0;
    
    // Pontuação baseada no percentual fora da meta
    pontuacao += percentualForaMetaTMA > 50 ? 20 : (percentualForaMetaTMA > 30 ? 10 : 0);
    pontuacao += percentualForaMetaTMR > 50 ? 20 : (percentualForaMetaTMR > 30 ? 10 : 0);
    
    // Pontuação baseada na tendência
    pontuacao += tempiora ? 20 : 0;
    
    // Adicionar apenas operadores com problemas significativos
    if (pontuacao >= 30) {
      operadoresProblematicos.push({
        nome: nome,
        nome_operador: nome, // Adicionar nome_operador para consistência
        mediaTMA: mediaTMA.toFixed(2),
        mediaTMR: mediaTMR.toFixed(2),
        percentualForaMetaTMA: percentualForaMetaTMA.toFixed(0),
        percentualForaMetaTMR: percentualForaMetaTMR.toFixed(0),
        tempiora,
        pontuacao,
        ultimoRegistro: ultimosRegistros[0] || null
      });
    }
  }
  
  // Ordenar por pontuação (do maior para o menor)
  return operadoresProblematicos.sort((a, b) => b.pontuacao - a.pontuacao);
}

// Função para exibir operadores que precisam de atenção
function exibirOperadoresComProblemas(operadores) {
  const painelAlerta = document.getElementById('painel-operadores-alerta');
  if (!painelAlerta) {
    return;
  }
  
  if (operadores.length === 0) {
    painelAlerta.innerHTML = '<div class="alerta-ok">✅ Todos os operadores estão com desempenho adequado! 👍</div>';
    return;
  }
  
  let html = '<h3>⚠️ Operadores que precisam de atenção</h3>';
  html += '<div class="grid-operadores-alerta">';
  
  operadores.forEach(op => {
    const corTMA = parseFloat(op.mediaTMA) > META_TMA ? 'red' : 'green';
    const corTMR = parseFloat(op.mediaTMR) > META_TMR ? 'red' : 'green';
    
    // Determinar a criticidade
    let criticidadeClass = '';
    let iconeCriticidade = '';
    
    if (op.pontuacao >= 70) {
      criticidadeClass = 'alta-criticidade';
      iconeCriticidade = '🔴';
    } else if (op.pontuacao >= 50) {
      criticidadeClass = 'media-criticidade';
      iconeCriticidade = '🟠';
    } else {
      criticidadeClass = 'baixa-criticidade';
      iconeCriticidade = '🟡';
    }
    
    // Ícones para status
    const tmaIcon = parseFloat(op.mediaTMA) > META_TMA ? '⚠️' : '✅';
    const tmrIcon = parseFloat(op.mediaTMR) > META_TMR ? '⚠️' : '✅';
    
    html += `
      <div class="card-operador-alerta ${criticidadeClass}">
        <h4>${iconeCriticidade} ${op.nome}</h4>
        <div class="metricas">
          <div class="metrica">
            <span>${tmaIcon} TMA Média</span>
            <strong style="color: ${corTMA}">${op.mediaTMA} min/cupom</strong>
            <small>${op.percentualForaMetaTMA}% dos registros fora da meta</small>
          </div>
          <div class="metrica">
            <span>${tmrIcon} TMR Média</span>
            <strong style="color: ${corTMR}">${op.mediaTMR} seg/item</strong>
            <small>${op.percentualForaMetaTMR}% dos registros fora da meta</small>
          </div>
        </div>
        ${op.tempiora ? '<div class="tendencia-negativa">⚠️ Tendência de piora nos últimos registros</div>' : ''}
        <div class="recomendacao">
          <strong>📋 Ação recomendada:</strong>
          ${gerarRecomendacao(op)}
        </div>
        <div class="card-operador-footer">
          <button class="ver-registros-btn" onclick="verRegistrosOperador('${op.nome_operador}')">📊 Ver todos os registros</button>
        </div>
      </div>
    `;
  });
  
  html += '</div>';
  
  console.log('HTML gerado para o painel:', html.substring(0, 150) + '...');
  
  // Aplicar o HTML ao painel de alerta
  painelAlerta.innerHTML = html;
  
  // Verificar se o HTML foi aplicado corretamente
  console.log('HTML final do painel:', painelAlerta.innerHTML.substring(0, 150) + '...');
}

// Função para gerar recomendações
function gerarRecomendacao(operador) {
  if (operador.mediaTMA > META_TMA && operador.mediaTMR > META_TMR) {
    return 'Orientar sobre agilidade e realizar acompanhamento semanal dos tempos.';
  } else if (operador.mediaTMA > META_TMA) {
    return 'Orientar sobre agilidade e realizar acompanhamento semanal dos tempos.';
  } else if (operador.mediaTMR > META_TMR) {
    return 'Orientar sobre agilidade e realizar acompanhamento semanal dos tempos.';
  } else if (operador.tempiora) {
    return 'Orientar sobre agilidade e realizar acompanhamento semanal dos tempos.';
  }
  
  return 'Orientar sobre agilidade e realizar acompanhamento semanal dos tempos.';
}

// Função para inicializar o painel de alerta dos operadores
function inicializarPainelAlerta() {
  console.log('Inicializando painel de alerta dos operadores...');
  
  const painelAlerta = document.getElementById('painel-operadores-alerta');
  if (!painelAlerta) {
    console.error('Elemento painel-operadores-alerta não encontrado durante inicialização!');
    return;
  }
  
  // Verificar se estamos na página de admin
  if (!window.location.pathname.includes('admin')) {
    console.log('Não estamos na página de admin, não inicializando painel de alerta');
    return;
  }
  
  // Verificar se o usuário é admin
  if (!is_admin) {
    console.log('Usuário não é admin, não inicializando painel de alerta');
    painelAlerta.innerHTML = '<div class="erro-admin">Você não tem permissão para acessar este painel</div>';
    return;
  }
  
  // Mostrar mensagem de carregamento
  painelAlerta.innerHTML = '<div class="carregando">Iniciando análise de operadores...</div>';
  
  // Carregar dados dos operadores
  setTimeout(() => {
    console.log('Carregando dados de operadores com delay...');
    carregarRegistrosAdmin();
  }, 1000);
  
  // Configurar atualização periódica
  setInterval(() => {
    console.log('Atualizando dados automaticamente...');
    carregarRegistrosAdmin();
  }, 300000); // Atualizar a cada 5 minutos
}

// Adicionar evento para inicializar o painel quando a página admin for carregada
if (window.location.pathname.includes('admin')) {
  window.addEventListener('load', inicializarPainelAlerta);
}

// Função para filtrar operadores pelo nome
function filtrarOperadoresPorNome(termoPesquisa) {
  const painelAlerta = document.getElementById('painel-operadores-alerta');
  if (!painelAlerta || !termoPesquisa) return;
  
  termoPesquisa = termoPesquisa.toLowerCase().trim();
  
  // Se a pesquisa estiver vazia, exibir todos os operadores problemáticos novamente
  if (termoPesquisa === '') {
    exibirOperadoresComProblemas(operadoresProblematicos);
    return;
  }
  
  // Obter todos os operadores únicos dos registros
  const todosOperadores = [...new Set(registrosAdmin.map(reg => reg.nome_operador))];
  
  // Filtrar operadores que correspondem ao termo de pesquisa
  const operadoresFiltrados = todosOperadores
    .filter(nome => nome && nome.toLowerCase().includes(termoPesquisa))
    .map(nome => {
      // Obter registros deste operador
      const registrosOperador = registrosAdmin.filter(reg => reg.nome_operador === nome);
      
      // Calcular métricas
      const tmas = registrosOperador.map(reg => parseFloat(reg.tma));
      const tmrs = registrosOperador.map(reg => parseFloat(reg.tmr));
      
      const mediaTMA = (tmas.reduce((sum, val) => sum + val, 0) / tmas.length).toFixed(2);
      const mediaTMR = (tmrs.reduce((sum, val) => sum + val, 0) / tmrs.length).toFixed(2);
      
      const registrosForaMetaTMA = tmas.filter(tma => tma > META_TMA).length;
      const registrosForaMetaTMR = tmrs.filter(tmr => tmr > META_TMR).length;
      
      const percentualForaMetaTMA = ((registrosForaMetaTMA / tmas.length) * 100).toFixed(1);
      const percentualForaMetaTMR = ((registrosForaMetaTMR / tmrs.length) * 100).toFixed(1);
      
      // Calcular pontuação de criticidade (0-100)
      const pontuacaoTMA = (mediaTMA > META_TMA) ? 
        Math.min(100, (mediaTMA / META_TMA - 1) * 100) : 0;
      const pontuacaoTMR = (mediaTMR > META_TMR) ? 
        Math.min(100, (mediaTMR / META_TMR - 1) * 100) : 0;
      const pontuacaoPercTMA = parseFloat(percentualForaMetaTMA);
      const pontuacaoPercTMR = parseFloat(percentualForaMetaTMR);
      
      const pontuacao = (pontuacaoTMA * 0.3 + pontuacaoTMR * 0.3 + 
                       pontuacaoPercTMA * 0.2 + pontuacaoPercTMR * 0.2).toFixed(1);
      
      // Verificar tendência de piora
      const ultimosRegistros = registrosOperador
        .sort((a, b) => {
          if (!a.data_registro && !b.data_registro) return 0;
          if (!a.data_registro) return 1;
          if (!b.data_registro) return -1;
          return new Date(b.data_registro) - new Date(a.data_registro);
        })
        .slice(0, Math.min(5, registrosOperador.length));
      
      const primeirosRegistros = registrosOperador
        .sort((a, b) => {
          if (!a.data_registro && !b.data_registro) return 0;
          if (!a.data_registro) return 1;
          if (!b.data_registro) return -1;
          return new Date(a.data_registro) - new Date(b.data_registro);
        })
        .slice(0, Math.min(5, registrosOperador.length));
      
      const mediaTMARecente = ultimosRegistros.reduce((sum, reg) => sum + parseFloat(reg.tma), 0) / ultimosRegistros.length;
      const mediaTMAInicial = primeirosRegistros.reduce((sum, reg) => sum + parseFloat(reg.tma), 0) / primeirosRegistros.length;
      
      const mediaTMRRecente = ultimosRegistros.reduce((sum, reg) => sum + parseFloat(reg.tmr), 0) / ultimosRegistros.length;
      const mediaTMRInicial = primeirosRegistros.reduce((sum, reg) => sum + parseFloat(reg.tmr), 0) / primeirosRegistros.length;
      
      const tempiora = (mediaTMARecente > mediaTMAInicial * 1.1) || (mediaTMRRecente > mediaTMRInicial * 1.1);
      
      return {
        nome: nome,
        nome_operador: nome, // Adicionar nome_operador para consistência
        mediaTMA,
        mediaTMR,
        percentualForaMetaTMA,
        percentualForaMetaTMR,
        pontuacao,
        tempiora,
        registros: registrosOperador
      };
    });
  
  // Ordenar operadores por pontuação (criticidade)
  operadoresFiltrados.sort((a, b) => b.pontuacao - a.pontuacao);
  
  // Exibir operadores filtrados
  exibirOperadoresComProblemas(operadoresFiltrados);
}

// Função para exibir todos os registros de um operador
function verRegistrosOperador(nomeOperador) {
  console.log('Função verRegistrosOperador chamada para:', nomeOperador);
  console.log('registrosAdmin disponíveis:', registrosAdmin ? registrosAdmin.length : 0);
  
  if (!nomeOperador) {
    console.error('Nome do operador não fornecido');
    alert('Erro: Nome do operador não fornecido');
    return;
  }
  
  if (!registrosAdmin || registrosAdmin.length === 0) {
    console.error('Não há registros disponíveis em registrosAdmin');
    alert('Não há registros disponíveis para análise');
    return;
  }
  
  // Verificar a estrutura dos registros
  console.log('Amostra de registros:', registrosAdmin.slice(0, 2));
  
  // Filtrar registros do operador
  const registrosOperador = registrosAdmin.filter(reg => {
    console.log(`Comparando '${reg.nome_operador}' com '${nomeOperador}'`);
    return reg.nome_operador && nomeOperador && 
           reg.nome_operador.toLowerCase() === nomeOperador.toLowerCase();
  });
  
  console.log('Registros encontrados para o operador:', registrosOperador.length);
  console.log('Exemplo de registro:', registrosOperador.length > 0 ? registrosOperador[0] : 'Nenhum registro');
  
  if (registrosOperador.length === 0) {
    alert(`Não foram encontrados registros para o operador: ${nomeOperador}`);
    return;
  }
  
  // Ordenar registros por data (mais recentes primeiro)
  registrosOperador.sort((a, b) => {
    if (!a.data_registro && !b.data_registro) return 0;
    if (!a.data_registro) return 1;
    if (!b.data_registro) return -1;
    return new Date(b.data_registro) - new Date(a.data_registro);
  });
  
  // Calcular estatísticas
  const tmas = registrosOperador.map(reg => parseFloat(reg.tma || 0));
  const tmrs = registrosOperador.map(reg => parseFloat(reg.tmr || 0));
  
  // Verificar os campos dos registros
  console.log("Exemplo de registro:", registrosOperador[0]);
  
  const mediaTMA = tmas.length > 0 ? (tmas.reduce((sum, val) => sum + val, 0) / tmas.length).toFixed(2) : "0.00";
  const mediaTMR = tmrs.length > 0 ? (tmrs.reduce((sum, val) => sum + val, 0) / tmrs.length).toFixed(2) : "0.00";
  const mediaTempoConexao = "N/A";
  const mediaChamadas = "N/A";
  
  const totalRegistros = registrosOperador.length;
  const registrosForaMetaTMA = tmas.filter(tma => tma > META_TMA).length;
  const registrosForaMetaTMR = tmrs.filter(tmr => tmr > META_TMR).length;
  
  const percentualForaMetaTMA = totalRegistros > 0 ? ((registrosForaMetaTMA / totalRegistros) * 100).toFixed(1) : "0.0";
  const percentualForaMetaTMR = totalRegistros > 0 ? ((registrosForaMetaTMR / totalRegistros) * 100).toFixed(1) : "0.0";
  
  // Preencher título do modal
  document.getElementById('modal-titulo').textContent = `Registros de ${nomeOperador}`;
  
  // Preencher estatísticas
  const estatisticasHTML = `
    <div class="estat-card">
      <div class="estat-titulo">TMA Média</div>
      <div class="estat-valor ${parseFloat(mediaTMA) > META_TMA ? 'fora-meta' : 'dentro-meta'}">${mediaTMA} min/cupom</div>
      <div class="estat-info">${percentualForaMetaTMA}% dos registros fora da meta</div>
    </div>
    <div class="estat-card">
      <div class="estat-titulo">TMR Média</div>
      <div class="estat-valor ${parseFloat(mediaTMR) > META_TMR ? 'fora-meta' : 'dentro-meta'}">${mediaTMR} seg/item</div>
      <div class="estat-info">${percentualForaMetaTMR}% dos registros fora da meta</div>
    </div>
    <div class="estat-card">
      <div class="estat-titulo">Total de Registros</div>
      <div class="estat-valor">${totalRegistros}</div>
      <div class="estat-info">Histórico completo</div>
    </div>
    <div class="estat-card">
      <div class="estat-titulo">Último Registro</div>
      <div class="estat-valor">${registrosOperador.length > 0 ? formatarDataSegura(registrosOperador[0].data_registro) : 'N/A'}</div>
      <div class="estat-info">Data mais recente</div>
    </div>
  `;
  
  document.getElementById('operador-estatisticas').innerHTML = estatisticasHTML;
  
  // Preencher tabela de registros
  let tabelaHTML = '';
  
  registrosOperador.forEach(reg => {
    const data = formatarDataSegura(reg.data_registro);
    const tma = reg.tma || 'N/A';
    const tmr = reg.tmr || 'N/A';
    
    const tmaClass = parseFloat(tma) > META_TMA ? 'fora-meta' : 'dentro-meta';
    const tmrClass = parseFloat(tmr) > META_TMR ? 'fora-meta' : 'dentro-meta';
    
    tabelaHTML += `
      <tr>
        <td>${data}</td>
        <td class="${tmaClass}">${tma}</td>
        <td class="${tmrClass}">${tmr}</td>
        <td>${reg.tempo_conexao || 'N/A'}</td>
        <td>${reg.chamadas || 'N/A'}</td>
      </tr>
    `;
  });
  
  document.getElementById('tabela-registros-corpo').innerHTML = tabelaHTML;
  
  // Exibir modal
  document.getElementById('modal-registros').style.display = 'flex';
}

// Função para fechar o modal de registros
function fecharModalRegistros() {
  document.getElementById('modal-registros').style.display = 'none';
}

// Função para formatar data de forma segura
function formatarDataSegura(dataStr) {
  if (!dataStr) return 'Data não disponível';
  
  try {
    const data = new Date(dataStr);
    if (isNaN(data.getTime())) {
      return 'Data inválida';
    }
    return data.toLocaleDateString('pt-BR');
  } catch (error) {
    console.error('Erro ao formatar data:', error, dataStr);
    return 'Erro na data';
  }
}