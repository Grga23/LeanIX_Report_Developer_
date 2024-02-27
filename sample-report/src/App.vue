<template>
  <div class="container mx-auto h-screen">
    <div class="flex flex-wrap items-start justify-center -mx-8 ">
      <div class="flex flex-col items-center px-8">
        <span class="text-3xl font-bold uppercase py-4">Facets</span>
        <pre>{{facetResultIndex}}</pre>
      </div>
      <div class="flex flex-col items-center px-8">
        <span class="text-3xl font-bold uppercase py-4">GraphQL</span>
        <pre>{{graphQLResultIndex}}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import '@leanix/reporting'
import { ref, watch } from 'vue'

// Reactive variables
const factSheetTypes = ref([])
const facetResultIndex = ref({})
const graphQLResultIndex = ref({})
const selectedFactSheetType = ref('')

// Initialize report
const initializeReport = async () => {
  const setup = await lx.init()
  factSheetTypes.value = Object.keys(setup.settings.dataModel.factSheets)
  graphQLResultIndex.value = factSheetTypes.value.reduce((acc, type) => ({ ...acc, [type]: null }), {})

  const facets = factSheetTypes.value.map((type, key) => ({
    key: key.toString(),
    fixedFactSheetType: type,
    attributes: ['completion { completion }'],
    facetFiltersChangedCallback: async filter => {
      graphQLResultIndex.value[type] = await fetchGraphQLData(type, filter)
    },
    callback: factSheets => {
      const count = factSheets.length
      const averageCompletion = ((factSheets.reduce((sum, { completion }) => sum + completion.completion, 0) / count) * 100).toFixed(2) + '%'
      facetResultIndex.value[type] = { label: lx.translateFactSheetType(type, 'plural'), count, averageCompletion }
    }
  }))

  lx.ready({ facets })
}

// Fetch data from GraphQL
const fetchGraphQLData = async (factSheetType, filter) => {
  const { facets: facetFilters, fullTextSearchTerm: fullTextSearch, directHits } = filter
  const mappedFilter = { facetFilters, fullTextSearch, ids: directHits.map(({ id }) => id) }
  const query = '{allFactSheets(factSheetType: Application) {edges {node {displayName ... on Application { relApplicationToITComponent { edges {node {costTotalAnnual factSheet {displayName }}}}}}}}}' 

  const queryResult = await lx.executeGraphQL(query, { filter: mappedFilter })
    .then(({ allFactSheets }) => {
      console.log(allFactSheets)
      const factSheets = allFactSheets.edges.map(({ node }) => node)
      console.log(factSheets[0].relApplicationToITComponent.edges[0].node.costTotalAnnual)
      const count = factSheets.length
      const annualValuesPerSoftware = factSheets.map(factSheet => {
          return factSheet.relApplicationToITComponent.edges.map(edge => {
            return {
              displayName: factSheet.displayName,
              costTotalAnnual: edge.node.costTotalAnnual
    };
  });
}).flat();
console.log(annualValuesPerSoftware)
      
      /*const costTotalAnnualValues = factSheets.map(factSheet => {
        return factSheet.relApplicationToITComponent.edges.map(edge => {
    return edge.node.costTotalAnnual;
  });
});
console.log(costTotalAnnualValues)
*/ 
      return { label: lx.translateFactSheetType(factSheetType, 'plural'), count, annualValuesPerSoftware}
    })
  return queryResult
}

/*
// Watch for changes in selectedFactSheetType and update data accordingly
watch(selectedFactSheetType, async selectedType => {
  if (selectedType && facetResultIndex.value[selectedType] === undefined) {
    await fetchGraphQLData(selectedType, { facets: [], fullTextSearchTerm: '', directHits: [] })
  }
})

// Handle filter change
const handleFilterChange = () => {
  if (selectedFactSheetType.value && facetResultIndex.value[selectedFactSheetType.value] === undefined) {
    fetchGraphQLData(selectedFactSheetType.value, { facets: [], fullTextSearchTerm: '', directHits: [] })
  }
}
*/ 
// Initialize report
initializeReport()



</script>
