import { createContext, useContext, useEffect, useState } from 'react'
import { useEntities } from '../hooks/useEntities'

const EntityContext = createContext(null)

export function EntityProvider({ children }) {
  const [entityId, setEntityId] = useState(() => {
    const saved = localStorage.getItem('selectedEntityId')
    return saved ? Number(saved) : null
  })

  const { data: entities = [], isLoading, error, refetch } = useEntities()

  useEffect(() => {
    if (entities.length && !entityId) {
      setEntityId(entities[0].id)
    }
  }, [entities, entityId])

  useEffect(() => {
    if (entityId) localStorage.setItem('selectedEntityId', String(entityId))
  }, [entityId])

  const entity = entities.find((e) => e.id === entityId) || null

  return (
    <EntityContext.Provider
      value={{ entityId, setEntityId, entity, entities, isLoading, error, refetch }}
    >
      {children}
    </EntityContext.Provider>
  )
}

export const useEntity = () => {
  const ctx = useContext(EntityContext)
  if (!ctx) throw new Error('useEntity must be used within EntityProvider')
  return ctx
}
