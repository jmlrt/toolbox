// Disable all the Jenkins jobs
import hudson.model.*

for(item in Hudson.instance.items) {
  println("Disabled job: " + item.name + '\n')
  item.disabled=true
  item.save()
}

def queue = Hudson.instance.queue
println "Queue contains ${queue.items.length} items"
queue.clear()
println "Queue cleared"
