// Seletores atualizados dinamicamente via Heurística e Inteligência DOM
const SELETORES = {
    classes: {
        textoPontosCard: '.text-itemHeader', 
        textoMetadata: '.text-metadata'
    },
    elementos: {
        perfilBotao: 'button[aria-label="Exibir perfil"] p',
        inputValorCustomizado: 'input[type="text"]'
    },
    validacoes: {
        placeholderSemPontos: '—'
    }
};

function extrairPontosPorTexto(elementoTexto) {
    if (!elementoTexto || elementoTexto.includes('—')) return 0;
    return parseInt(elementoTexto.replace(/\D/g, '')) || 0;
}
