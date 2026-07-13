import { supabase } from './supabase'

function asBucketList(bucket: string | string[]) {
  return Array.isArray(bucket) ? bucket : [bucket]
}

export async function uploadFileToBucket(bucket: string | string[], path: string, file: File) {
  const buckets = asBucketList(bucket)

  for (const bucketName of buckets) {
    try {
      const { data, error } = await supabase.storage.from(bucketName).upload(path, file, { upsert: true })
      if (!error) return { data, error: null }
      if (error?.message) return { data: null, error: new Error(error.message) }
    } catch (error) {
      if (error instanceof Error) return { data: null, error }
    }
  }

  return { data: null, error: new Error('No fue posible subir el archivo en los buckets configurados') }
}

export async function getSignedUrlForPath(bucket: string | string[], path: string, expires = 300) {
  if (!path) return { signedURL: null, error: 'no-path' }

  const buckets = asBucketList(bucket)
  let lastError: unknown = null

  for (const bucketName of buckets) {
    try {
      const { data, error } = await supabase.storage.from(bucketName).createSignedUrl(path, expires)
      if (!error) return { signedURL: data.signedUrl, error: null }
      lastError = error
    } catch (error) {
      lastError = error
    }
  }

  return { signedURL: null, error: lastError instanceof Error ? lastError : new Error('No fue posible generar la URL firmada') }
}

export async function removeFileFromBucket(bucket: string | string[], path: string) {
  const buckets = asBucketList(bucket)

  for (const bucketName of buckets) {
    try {
      const { data, error } = await supabase.storage.from(bucketName).remove([path])
      if (!error) return { data, error: null }
    } catch {
      // Intenta con el siguiente bucket si este falla
    }
  }

  return { data: null, error: new Error('No fue posible eliminar el archivo en los buckets configurados') }
}
