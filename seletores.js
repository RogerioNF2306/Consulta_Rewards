// Seletores extraídos cirurgicamente da estrutura HTML fornecida do Microsoft Rewards
const SELETORES = {
    classes: {
        textoPontosCard: '.text-pageHeader', // Presente nos blocos de R$5, R$15, R$30 e no customizado
        textoMetadata: '.text-metadata'
    },
    elementos: {
        perfilBotao: 'button[aria-label="Exibir perfil"] p',
        inputValorCustomizado: 'input[type="text"]' // Input contido no span wrapper do valor personalizado
    },
    validacoes: {
        placeholderSemPontos: '—'
    }
};

function extrairPontosPorTexto(elementoTexto) {
    if (!elementoTexto || elementoTexto.includes('—')) return 0;
    return parseInt(elementoTexto.replace(/\D/g, '')) || 0;
}
