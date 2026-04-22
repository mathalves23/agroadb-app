import { useNavigate } from 'react-router-dom'

import { EmptyState } from '@/components/EmptyState'
import { PanelListLoader } from '@/components/Loading'
import { integrations } from '@/pages/settings/catalog'
import { ConectaInfoBanner } from '@/pages/settings/ConectaInfoBanner'
import { GovernanceSettingsCard } from '@/pages/settings/GovernanceSettingsCard'
import { IntegrationCatalogGrid } from '@/pages/settings/IntegrationCatalogGrid'
import { IntegrationCategoryStats } from '@/pages/settings/IntegrationCategoryStats'
import { IntegrationCategoryTabs } from '@/pages/settings/IntegrationCategoryTabs'
import { SettingsHeader } from '@/pages/settings/SettingsHeader'
import { SettingsSetupGuide } from '@/pages/settings/SettingsSetupGuide'
import { useIntegrationSettings } from '@/pages/settings/useIntegrationSettings'

export default function SettingsPage() {
  const navigate = useNavigate()
  const {
    counts,
    filteredIntegrations,
    getStatus,
    govHumanReview,
    govMutation,
    govOrgId,
    govRefUrl,
    integrationQuery,
    orgs,
    selectedCategory,
    setGovHumanReview,
    setGovOrgId,
    setGovRefUrl,
    setSelectedCategory,
  } = useIntegrationSettings()

  return (
    <div className="space-y-6">
      <SettingsHeader
        integrationCount={integrations.length}
        isLoading={integrationQuery.isLoading}
        onBack={() => navigate(-1)}
        onRefresh={() => void integrationQuery.refetch()}
      />

      {integrationQuery.isLoading ? (
        <PanelListLoader
          message="A carregar estado das integrações..."
          subMessage="A sincronizar com o backend para indicar APIs ativas e credenciais."
        />
      ) : integrationQuery.isError ? (
        <EmptyState
          variant="embedded"
          illustration="settings"
          title="Não foi possível obter o estado das integrações"
          description={
            integrationQuery.error instanceof Error
              ? integrationQuery.error.message
              : 'Verifique a ligação ao servidor e tente novamente.'
          }
          action={{
            label: 'Tentar novamente',
            onClick: () => void integrationQuery.refetch(),
          }}
        />
      ) : null}

      {!integrationQuery.isLoading && !integrationQuery.isError && (
        <>
          <IntegrationCategoryStats counts={counts} getStatus={getStatus} items={integrations} />
          <IntegrationCategoryTabs
            counts={counts}
            selectedCategory={selectedCategory}
            onChange={setSelectedCategory}
          />
          {(selectedCategory === 'conecta' || selectedCategory === 'all') && <ConectaInfoBanner />}
          <IntegrationCatalogGrid getStatus={getStatus} items={filteredIntegrations} />
        </>
      )}

      <GovernanceSettingsCard
        govHumanReview={govHumanReview}
        govMutationError={govMutation.isError}
        govMutationPending={govMutation.isPending}
        govOrgId={govOrgId}
        govRefUrl={govRefUrl}
        onChangeHumanReview={setGovHumanReview}
        onChangeOrg={setGovOrgId}
        onChangeRefUrl={setGovRefUrl}
        onSave={() => govMutation.mutate()}
        orgs={orgs}
      />

      <SettingsSetupGuide />
    </div>
  )
}
